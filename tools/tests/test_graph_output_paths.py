"""Real metadata-link faults plus native external-storage/worktree regressions."""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile


def run(argv, root, env, expected=0):
    p=subprocess.run([str(x) for x in argv],cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',timeout=120)
    if expected is not None: assert p.returncode==expected, (p.returncode, 'local fixture command failed')
    return p


def invoke(cli, root, env, action, fresh):
    p=run([sys.executable,'-E','-B',cli,action,'--cwd',root,'--require-both','--no-subprojects'],root,env,expected=0 if fresh else 2)
    value=json.loads(p.stdout);assert value['fresh']==fresh,value
    return value


def snapshot(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}


def directory_link(target, link):
    if os.name=='nt':
        import _winapi
        _winapi.CreateJunction(str(target),str(link));assert link.is_junction()
    else: link.symlink_to(target,target_is_directory=True)


def file_link(target, link):
    try:
        link.symlink_to(target);return 'file_symlink'
    except OSError:
        os.link(target,link);return 'file_hardlink'


def unlink_directory(link):
    if os.name=='nt': link.rmdir()
    else: link.unlink()


PY_PROBE=r'''
import contextlib,importlib.util,json,os,runpy,sys
from pathlib import Path
cli,root,name,mode,target,source=map(str,sys.argv[1:])
root,target,source=Path(root),Path(target),Path(source)
sys.path.insert(0,str(Path(cli).parent))
import graph_freshness_cli as m
import graph_paths as gp
counts={'sqlite':0,'native':0,'content':0,'output':0}
def fail(kind):
    counts[kind]+=1
    raise AssertionError('unexpected_metadata_io')
m.sqlite3.connect=lambda *a,**k:fail('sqlite')
original_open,original_mkdir=Path.open,Path.mkdir
def same_tree(path):
    return Path(os.path.abspath(path)).is_relative_to(target)
def open_trap(path,*a,**k):
    if same_tree(path):fail('content')
    return original_open(path,*a,**k)
def mkdir_trap(path,*a,**k):
    if same_tree(path):fail('output')
    return original_mkdir(path,*a,**k)
Path.open,Path.mkdir=open_trap,mkdir_trap
caught=False
try:
    if mode=='inspect':
        filename='codegraph.db' if name=='codegraph' else 'graph.db'
        m.inspect_graph(name,{'db':str(target/filename),'hashes':{}},root)
    elif mode=='lock':
        with m.advisory_lock(root):pass
    elif mode=='backup':
        m.time.time_ns=lambda:1
        m.os.getpid=lambda:42
        m.backup(source,Path(m.run(['git','rev-parse','--absolute-git-dir'],root)).resolve(),'fixture',source.parent)
    else:
        import code_review_graph.incremental as inc
        from code_review_graph.graph import GraphStore
        inc.get_db_path=lambda *a,**k:fail('native')
        GraphStore.__init__=lambda *a,**k:fail('native')
        namespace=runpy.run_path(str(Path(cli).parent/'graph_crg_bridge.py'))
        sys.argv=['bridge',str(root),'build']
        namespace['main']()
except gp.PathBoundaryError:
    caught=True
except AssertionError:
    pass
print(json.dumps({'boundary_rejected':caught,'io_counts':counts}))
'''

NODE_PROBE=r'''
const [dist, bridge, root, prefix] = process.argv.slice(1);
const fs=require('fs'),path=require('path');
const output=process.stdout.write.bind(process.stdout);
const sdk=require(path.join(dist,'index.js')).default;
const counts={native:0,content:0,output:0};
for(const method of ['open','init']) sdk[method]=async()=>{counts.native++;throw Error('native_trap');};
const matches=p=>typeof p==='string' && (path.resolve(p)===path.resolve(prefix)||path.resolve(p).startsWith(path.resolve(prefix)+path.sep));
for(const method of ['readFileSync','writeFileSync','mkdirSync','openSync','unlinkSync','renameSync']) {
 const original=fs[method];fs[method]=function(p,...rest){if(matches(p)){counts[method==='readFileSync'?'content':'output']++;throw Error('io_trap');}return original.call(this,p,...rest);};
}
process.on('exit',()=>output(JSON.stringify({io_counts:counts})+'\n'));
process.argv=[process.execPath,bridge,dist,root,'build'];require(bridge);
'''


def python_probe(cli, root, env, name, mode, target, source):
    config=json.loads((cli.parent/'graph-refresh.json').read_text())
    python=config['crg_python'] if mode=='native' else sys.executable
    p=run([python,'-E','-B','-c',PY_PROBE,cli,root,name,mode,target,source],root,env)
    value=json.loads(p.stdout)
    assert value['boundary_rejected'] and not any(value['io_counts'].values()),value
    return value


def node_probe(cli, root, env, command, target):
    p=run([*command[:3],'-e',NODE_PROBE,command[-1],cli.parent/'graph_cg_bridge.cjs',root,target],root,env,expected=1)
    value=json.loads(p.stdout.splitlines()[-1]);assert not any(value['io_counts'].values()),value
    return value


def exercise(cli, base, history_source):
    base.mkdir();root=base/'repo';root.mkdir();outside=base/'outside';outside.mkdir()
    env=dict(os.environ,CRG_HOME=str(base/'native-home'),GIT_OPTIONAL_LOCKS='0',DO_NOT_TRACK='1',CODEGRAPH_NO_UPDATE_CHECK='1',CODEGRAPH_NO_DOWNLOAD='1',NO_COLOR='1')
    env.pop('CRG_DATA_DIR',None);env.pop('CODEGRAPH_DIR',None)
    run(['git','init','--quiet',root],base,env)
    (root/'a.py').write_text('def output_before():\n    return 1\n',encoding='utf-8')
    (root/'.gitignore').write_text('.codegraph/\n.code-review-graph/\n',encoding='utf-8')
    run(['git','add','a.py','.gitignore'],root,env)
    invoke(cli,root,env,'status',False);assert not (base/'native-home').exists()
    initial=invoke(cli,root,env,'ensure',True)
    spec=importlib.util.spec_from_file_location('output_cli',cli);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    commands,_=module.discover(json.loads((cli.parent/'graph-refresh.json').read_text()),root)
    (outside/'sentinel.txt').write_bytes(b'fixture-owned-unchanged-sentinel')
    # Actual valid external DBs copied through the SQLite backup API.
    for name,rel in [('codegraph','.codegraph/codegraph.db'),('code-review-graph','.code-review-graph/graph.db')]:
        with contextlib.closing(sqlite3.connect((root/rel).as_uri()+'?mode=ro',uri=True)) as src,contextlib.closing(sqlite3.connect(outside/(name+'.db'))) as dst:src.backup(dst)
    cases=[]
    for name,folder,dbfile in [('codegraph','.codegraph','codegraph.db'),('code-review-graph','.code-review-graph','graph.db')]:
        data=root/folder;held=base/('held-'+name)
        # Both missing and existing valid DB through a real outward junction.
        for existing in (False,True):
            data.rename(held)
            target=outside/('dir-'+name+str(existing));target.mkdir()
            (target/'sentinel.txt').write_bytes(b'unchanged')
            if existing:(target/dbfile).write_bytes((outside/(name+'.db')).read_bytes())
            directory_link(target,data);before=snapshot(outside)
            try:
                python_probe(cli,root,env,name,'inspect',data,root/'.codegraph/codegraph.db')
                if name=='codegraph':node_probe(cli,root,env,commands[name],data)
                else:python_probe(cli,root,env,name,'native',data,root/'.codegraph/codegraph.db')
                invoke(cli,root,env,'ensure',False);assert snapshot(outside)==before
                cases.append({'case':name+'_directory_link','existing_db':existing,'outside_unchanged':True,'read_native_write_traps_zero':True})
            finally:unlink_directory(data);held.rename(data)
        leaves=[dbfile,'.gitignore',dbfile+'-wal',dbfile+'-shm',dbfile+'-journal']
        if name=='codegraph':leaves.append('codegraph.lock')
        for i,leaf in enumerate(leaves):
            candidate=data/leaf;saved=base/('held-leaf-'+name+str(i))
            if candidate.exists():candidate.rename(saved)
            kind=file_link(outside/(name+'.db') if leaf==dbfile else outside/'sentinel.txt',candidate);before=snapshot(outside)
            try:
                python_probe(cli,root,env,name,'inspect',data,root/'.codegraph/codegraph.db')
                if name=='codegraph':node_probe(cli,root,env,commands[name],data)
                else:python_probe(cli,root,env,name,'native',data,root/'.codegraph/codegraph.db')
                assert snapshot(outside)==before
                cases.append({'case':name+'_'+leaf,'link_kind':kind,'outside_unchanged':True,'read_native_write_traps_zero':True})
            finally:
                candidate.unlink()
                if saved.exists():saved.rename(candidate)
    # Legacy source and every sidecar that native get_db_path can rename/unlink.
    for suffix in ('','-wal','-shm','-journal'):
        candidate=root/('.code-review-graph.db'+suffix);kind=file_link(outside/'sentinel.txt',candidate);before=snapshot(outside)
        try:
            python_probe(cli,root,env,'code-review-graph','native',root/'.code-review-graph',root/'.codegraph/codegraph.db')
            assert snapshot(outside)==before;cases.append({'case':'legacy'+suffix,'link_kind':kind,'outside_unchanged':True,'native_trap_zero':True})
        finally:candidate.unlink()
    git=Path(run(['git','rev-parse','--absolute-git-dir'],root,env).stdout.strip()).resolve()
    lock=git/'graph-freshness.lock';saved=base/'held-adapter-lock';lock.rename(saved)
    file_link(outside/'sentinel.txt',lock);before=snapshot(outside)
    try:python_probe(cli,root,env,'adapter','lock',lock,root/'.codegraph/codegraph.db');assert snapshot(outside)==before
    finally:lock.unlink();saved.rename(lock)
    cases.append({'case':'adapter_lock_alias','outside_unchanged':True,'open_write_traps_zero':True})
    backups=git/'graph-freshness-backups';held=base/'held-backups'
    if backups.exists():backups.rename(held)
    directory_link(outside,backups);before=snapshot(outside)
    try:python_probe(cli,root,env,'adapter','backup',backups,root/'.codegraph/codegraph.db');assert snapshot(outside)==before
    finally:
        unlink_directory(backups)
        if held.exists():held.rename(backups)
    cases.append({'case':'adapter_backup_directory_alias','outside_unchanged':True,'mkdir_sqlite_traps_zero':True})
    fixed=backups/'1-42';fixed.mkdir(parents=True,exist_ok=True)
    for suffix in ('','-wal','-shm','-journal'):
        candidate=fixed/('fixture.db'+suffix);kind=file_link(outside/'sentinel.txt',candidate);before=snapshot(outside)
        try:python_probe(cli,root,env,'adapter','backup',backups,root/'.codegraph/codegraph.db');assert snapshot(outside)==before
        finally:candidate.unlink()
        cases.append({'case':'adapter_backup_db'+suffix,'link_kind':kind,'outside_unchanged':True,'mkdir_sqlite_traps_zero':True})
    # Lexically internal mappings must not authorize their outward junction.
    home=base/'native-home';home.mkdir(exist_ok=True)
    internal=root/'.code-review-graph';held=base/'held-crg-internal';internal.rename(held);directory_link(outside,internal)
    try:
        for origin in ('environment','registry'):
            cfg=dict(env,CRG_DATA_DIR=str(internal))
            if origin=='registry':(home/'registry.json').write_text(json.dumps({'repos':[{'path':str(root.resolve()),'data_dir':str(internal)}]}),encoding='utf-8')
            before=snapshot(outside);python_probe(cli,root,cfg,'code-review-graph','native',internal,root/'.codegraph/codegraph.db');assert snapshot(outside)==before
            cases.append({'case':'internal_'+origin+'_alias','outside_unchanged':True})
    finally:
        (home/'registry.json').unlink(missing_ok=True);unlink_directory(internal);held.rename(internal)
    positives=[]
    for origin in ('environment','registry'):
        selected=base/('explicit-'+origin);cfg=dict(env,CRG_DATA_DIR=str(selected))
        if origin=='registry':
            cfg['CRG_DATA_DIR']=str(base/'lower-priority-env')
            (home/'registry.json').write_text(json.dumps({'repos':[{'path':str(root.resolve()),'data_dir':str(selected)}]}),encoding='utf-8')
        result=invoke(cli,root,cfg,'ensure',True)
        assert result['backends']['code-review-graph']['storage_origin']==origin
        assert (selected/'graph.db').is_file()
        (root/'new.py').write_text('def output_untracked_'+origin+'():\n    return 2\n',encoding='utf-8')
        invoke(cli,root,cfg,'status',False);result=invoke(cli,root,cfg,'refresh',True)
        with contextlib.closing(sqlite3.connect((selected/'graph.db').as_uri()+'?mode=ro',uri=True)) as db:assert db.execute("SELECT count(*) FROM nodes WHERE name=?",('output_untracked_'+origin,)).fetchone()[0]
        positives.append({'case':'explicit_'+origin,'real_ingestion':True,'native_origin_preserved':True})
        (home/'registry.json').unlink(missing_ok=True)
    # Valid legacy migration is retained; only fixture-owned regular files move.
    regular=root/'.code-review-graph';regular.rename(base/'held-normal-crg')
    (root/'.code-review-graph.db').write_bytes((outside/'code-review-graph.db').read_bytes())
    invoke(cli,root,env,'ensure',True);assert not (root/'.code-review-graph.db').exists()
    positives.append({'case':'regular_legacy_migration','real_ingestion':True})
    # Read existing local history into a new fixture clone; create no commits and
    # register no worktree against the real source repository.
    if history_source:
        clone=base/'history-clone';worktree=base/'worktree'
        run(['git','clone','--quiet','--no-checkout','--no-hardlinks',history_source,clone],base,env)
        run(['git','-C',clone,'worktree','add','--quiet','--detach','--no-checkout',worktree,'HEAD'],base,env)
        (worktree/'a.py').write_text('def output_worktree():\n    return 1\n',encoding='utf-8')
        (worktree/'.gitignore').write_text('.codegraph/\n.code-review-graph/\n',encoding='utf-8')
        run(['git','add','a.py','.gitignore'],worktree,env)
        actual_git=Path(run(['git','rev-parse','--absolute-git-dir'],worktree,env).stdout.strip()).resolve()
        assert not actual_git.is_relative_to(worktree.resolve()) and actual_git.is_relative_to(base.resolve())
        invoke(cli,worktree,env,'ensure',True)
        (worktree/'b.py').write_text('def output_worktree_untracked():\n    return 2\n',encoding='utf-8')
        invoke(cli,worktree,env,'refresh',True)
        assert (actual_git/'graph-freshness.lock').is_file() and (actual_git/'graph-freshness-backups').is_dir()
        positives.append({'case':'real_worktree_external_gitdir','real_ingestion':True,'no_new_commit_or_source_registration':True})
    return {'negative_cases':cases,'positive_cases':positives,'initial_default':initial,'fresh':True,'status_missing_registry_created':False,'worktree_tested':bool(history_source)}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cli',action='append',required=True);p.add_argument('--report',required=True);p.add_argument('--fixture-root');p.add_argument('--history-source');a=p.parse_args();report={}
    with tempfile.TemporaryDirectory(prefix='graph-output-',dir=a.fixture_root) as d:
        for i,value in enumerate(a.cli):
            cli=Path(value).resolve();report[str(cli)]=exercise(cli,Path(d)/str(i),a.history_source)
            Path(a.report).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            print('PASS '+cli.parent.parent.name+': '+str(len(report[str(cli)]['negative_cases']))+' real metadata alias cases, external registry/env, default/legacy'+('/worktree' if a.history_source else '')+' native ingestion',flush=True)
