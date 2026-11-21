"""Real installed-backend integration regression; creates only temporary Git repos.

python tools/tests/test_graph_freshness.py --cli tools/graph_freshness_cli.py --report <json>
No commits, mocks of graph ingestion, MCP, model calls or network installations.
"""
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
import time


def call(cli, action, root, expected=None):
    p = subprocess.run([sys.executable,'-B',str(cli),action,'--cwd',str(root),
                        '--require-both','--no-subprojects'],capture_output=True,text=True,
                       encoding='utf-8',timeout=600)
    data = json.loads(p.stdout)
    assert p.returncode in (0,2), (p.returncode,data)
    assert (p.returncode==0) == data['fresh'], data
    if expected is not None: assert data['fresh'] == expected, data
    return data


def query(root, symbol, present=True):
    for name,table in [('.codegraph/codegraph.db','nodes'),('.code-review-graph/graph.db','nodes')]:
        with contextlib.closing(sqlite3.connect((root/name).resolve().as_uri()+'?mode=ro',uri=True)) as db:
            count=db.execute(f'SELECT count(*) FROM {table} WHERE name=?',(symbol,)).fetchone()[0]
            assert bool(count)==present, (name,symbol,count,present)


def exercise(cli, root, faults=True):
    root.mkdir()
    subprocess.run(['git','init','--quiet',str(root)],check=True)
    (root/'.gitignore').write_text('.codegraph/\n.code-review-graph/\n',encoding='utf-8')
    (root/'a.py').write_text('def fixture_before_a():\n    return 1\n',encoding='utf-8')
    subprocess.run(['git','add','a.py','.gitignore'],cwd=root,check=True)
    before=call(cli,'status',root,False)
    assert not (root/'.codegraph').exists() and not (root/'.code-review-graph').exists()
    results={'missing_readonly':before,'initial':call(cli,'ensure',root,True)}
    query(root,'fixture_before_a')
    assert not (root/'.git/hooks/post-commit').exists()
    (root/'a.py').write_text('def fixture_after_b():\n    return 2\n',encoding='utf-8')
    (root/'new_dir').mkdir()
    (root/'new_dir/new_file.py').write_text('def fixture_untracked_b():\n    return 3\n',encoding='utf-8')
    results['stale_modified_untracked']=call(cli,'status',root,False)
    results['modified_untracked']=call(cli,'refresh',root,True)
    query(root,'fixture_after_b'); query(root,'fixture_untracked_b'); query(root,'fixture_before_a',False)
    # Native query/search supplement direct SQLite symbol/hash assertions.
    env=dict(os.environ, DO_NOT_TRACK='1', CODEGRAPH_NO_UPDATE_CHECK='1', CODEGRAPH_NO_DOWNLOAD='1', NO_COLOR='1')
    spec=importlib.util.spec_from_file_location('graph_cli',cli); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    config=json.loads((cli.parent/'graph-refresh.json').read_text())
    commands,_=module.discover(config,root)
    node_command=commands['codegraph']
    dist=Path(node_command[-1])
    cg=subprocess.run([*node_command[:3],str(dist/'bin/codegraph.js'),'query','fixture_untracked_b','--path',str(root),'--json'],cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',timeout=90)
    crg=subprocess.run([config['crg_python'],'-B','-m','code_review_graph','search','fixture_untracked_b','--repo',str(root)],cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',timeout=90)
    assert cg.returncode==0 and 'fixture_untracked_b' in cg.stdout
    assert crg.returncode==0 and 'fixture_untracked_b' in crg.stdout
    results['native_query_search']={'codegraph':True,'code_review_graph':True}
    # Same byte count and preserved mtime must still reach native extraction.
    file=root/'a.py'; stat=file.stat()
    file.write_bytes(file.read_bytes().replace(b'fixture_after_b',b'fixture_after_c'))
    os.utime(file,ns=(stat.st_atime_ns,stat.st_mtime_ns))
    results['same_size_mtime_stale']=call(cli,'status',root,False)
    results['same_size_mtime_refresh']=call(cli,'refresh',root,True)
    query(root,'fixture_after_c'); query(root,'fixture_after_b',False)
    (root/'new_dir/new_file.py').rename(root/'new_dir/renamed.py')
    results['renamed']=call(cli,'refresh',root,True)
    (root/'new_dir/renamed.py').unlink()
    results['deleted']=call(cli,'refresh',root,True)
    query(root,'fixture_untracked_b',False)
    snapshot={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ['.codegraph/codegraph.db','.code-review-graph/graph.db']}
    results['no_change']=call(cli,'ensure',root,True)
    assert not results['no_change']['operations']
    assert snapshot=={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in snapshot}
    if not faults:
        results['final']=call(cli,'status',root,True)
        return results
    results['nested_cwd_rejected']=call(cli,'status',root/'new_dir',False)
    assert results['nested_cwd_rejected']['error']=='cwd_must_be_exact_git_root'
    # Polluted inherited Python environment must not affect the pipx bridge.
    old_env={k:os.environ.get(k) for k in ('PYTHONHOME','PYTHONPATH')}
    try:
        os.environ['PYTHONHOME']=str(root/'not-python')
        os.environ['PYTHONPATH']=str(root/'not-modules')
        result,code=module.execute(argparse.Namespace(cwd=str(root),action='status',require_both=True,no_subprojects=True))
        assert code==0 and result['fresh']
        results['python_environment_isolated']=True
    finally:
        for k,v in old_env.items():
            if v is None: os.environ.pop(k,None)
            else: os.environ[k]=v
    # Adapter lock is shared by every independent installed copy.
    with module.advisory_lock(root):
        results['held_adapter_lock']=call(cli,'refresh',root,False)
        assert results['held_adapter_lock']['error']=='project_refresh_busy', results['held_adapter_lock']
    file.write_text('def fixture_after_d():\n    return 4\n',encoding='utf-8')
    native_lock=root/'.codegraph/codegraph.lock'
    native_lock.write_text('fixture-owned-lock\n',encoding='utf-8')
    results['native_lock']=call(cli,'refresh',root,False)
    assert native_lock.exists()
    native_lock.unlink()
    call(cli,'refresh',root,True)
    # Fault cases use a real previously built DB preimage, then restore it.
    db=root/'.codegraph/codegraph.db'; saved=root/'.codegraph/fixture-saved.db'
    db.rename(saved)
    results['missing_after_build']=call(cli,'status',root,False)
    assert not db.exists()
    db.write_bytes(b'not a sqlite database')
    results['corrupt_status']=call(cli,'status',root,False)
    results['corrupt_refresh']=call(cli,'refresh',root,False)
    assert db.read_bytes()==b'not a sqlite database'
    db.unlink(); db.touch()
    results['empty_status']=call(cli,'status',root,False)
    db.unlink(); saved.rename(db)
    # Execute real local ingestion then modify source before final verification.
    file.write_text('def fixture_after_e():\n    return 5\n',encoding='utf-8')
    native_bridge=module.bridge
    mutated=False
    def changing_bridge(command, repo, action, payload=None):
        nonlocal mutated
        value=native_bridge(command,repo,action,payload)
        if action!='scope' and not mutated:
            file.write_text('def fixture_after_f():\n    return 6\n',encoding='utf-8')
            mutated=True
        return value
    module.bridge=changing_bridge
    result,code=module.execute(argparse.Namespace(cwd=str(root),action='refresh',require_both=True,no_subprojects=True))
    assert code==2 and not result['fresh']
    assert all('source_changed_during_refresh' in s['reasons'] for s in result['backends'].values())
    results['source_mutation']=result
    call(cli,'refresh',root,True)
    results['final']=call(cli,'status',root,True)
    return results


def scope_contract(cli, root):
    """Extension recognition must not be confused with native extraction support."""
    root.mkdir()
    subprocess.run(['git','init','--quiet',str(root)],check=True)
    files={
        '.gitignore':'.codegraph/\n.code-review-graph/\n',
        'a.py':'def fixture_scope_tracked():\n    return 1\n',
        'empty.py':'',
        'config.yaml':'name: fixture-generic-yaml\n',
        'pnpm-lock.yaml':"lockfileVersion: '9.0'\n",
        'application.yaml':'spring:\n  application:\n    name: fixture-spring\nserver:\n  port: 8081\n',
        'playbooks/site.yml':'- hosts: localhost\n  tasks:\n    - name: fixture_ansible_task\n      ansible.builtin.debug:\n        msg: fixture\n',
        'playbooks/promoted.yml':'name: not-ansible-yet\n',
    }
    for rel,content in files.items():
        path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content,encoding='utf-8')
    subprocess.run(['git','add','.'],cwd=root,check=True)
    (root/'untracked.py').write_text('def fixture_scope_untracked():\n    return 2\n',encoding='utf-8')
    result=call(cli,'ensure',root,True)
    crg=result['backends']['code-review-graph']
    assert crg['excluded_files']=={'generic_yaml_not_supported_by_native_parser':2,'ansible_path_without_native_content_evidence':1},crg
    assert crg['expected_files']==5 and crg['files']==5,crg
    with contextlib.closing(sqlite3.connect((root/'.code-review-graph/graph.db').as_uri()+'?mode=ro',uri=True)) as db:
        actual={Path(p).relative_to(root).as_posix():h for p,h in db.execute("SELECT file_path,file_hash FROM nodes WHERE kind='File'")}
    assert set(actual)=={'a.py','empty.py','untracked.py','application.yaml','playbooks/site.yml'},actual
    assert actual['empty.py']==hashlib.sha256(b'').hexdigest()
    for rel,digest in actual.items(): assert digest==hashlib.sha256((root/rel).read_bytes()).hexdigest()
    query(root,'fixture_scope_untracked')
    # Supported code is still mandatory; exclusion cannot hide an untracked edit.
    (root/'untracked.py').write_text('def fixture_scope_untracked_new():\n    return 3\n',encoding='utf-8')
    stale=call(cli,'status',root,False)
    assert stale['backends']['code-review-graph']['modified']==1,stale
    call(cli,'refresh',root,True)
    query(root,'fixture_scope_untracked_new'); query(root,'fixture_scope_untracked',False)
    # Content-gated YAML must enter and leave the graph when native support changes.
    promoted=root/'playbooks/promoted.yml'
    promoted.write_text('- hosts: localhost\n  tasks:\n    - name: fixture_promoted_task\n      ansible.builtin.debug:\n        msg: promoted\n',encoding='utf-8')
    promoted_stale=call(cli,'status',root,False)
    assert promoted_stale['backends']['code-review-graph']['added']==1,promoted_stale
    call(cli,'refresh',root,True)
    with contextlib.closing(sqlite3.connect((root/'.code-review-graph/graph.db').as_uri()+'?mode=ro',uri=True)) as db:
        assert db.execute("SELECT count(*) FROM nodes WHERE kind='File' AND file_path=?",(promoted.as_posix(),)).fetchone()[0]==1
    promoted.write_text('name: generic-again\n',encoding='utf-8')
    demoted_stale=call(cli,'status',root,False)
    assert demoted_stale['backends']['code-review-graph']['removed']==1,demoted_stale
    demoted=call(cli,'refresh',root,True)
    with contextlib.closing(sqlite3.connect((root/'.code-review-graph/graph.db').as_uri()+'?mode=ro',uri=True)) as db:
        assert db.execute('SELECT count(*) FROM nodes WHERE file_path=?',(promoted.as_posix(),)).fetchone()[0]==0
    final=call(cli,'ensure',root,True)
    assert not final['operations']
    return {'initial_scope':result,'supported_untracked_stale':stale,'promoted_stale':promoted_stale,
            'demoted_stale':demoted_stale,'demoted':demoted,'final':final,
            'native_query_search':{'sqlite_actual_file_hashes':True,'empty_python_file_node':True,'spring_ansible_yaml_nodes':True}}


def boundary_contract(cli, root):
    """A tracked file under an escaping directory link must fail before reads."""
    root.mkdir()
    subprocess.run(['git','init','--quiet',str(root)],check=True)
    (root/'.gitignore').write_text('.codegraph/\n.code-review-graph/\n',encoding='utf-8')
    (root/'local.py').write_text('def fixture_boundary_local():\n    return 1\n',encoding='utf-8')
    linked=root/'linked';linked.mkdir()
    (linked/'a.py').write_text('def fixture_boundary_original():\n    return 1\n',encoding='utf-8')
    subprocess.run(['git','add','.'],cwd=root,check=True)
    outside=root.parent/(root.name+'-outside');outside.mkdir()
    (outside/'a.py').write_text('def fixture_outside_must_not_be_read():\n    return 9\n',encoding='utf-8')
    (linked/'a.py').unlink();linked.rmdir()
    if os.name=='nt':
        import _winapi
        _winapi.CreateJunction(str(outside),str(linked))
        assert linked.is_junction()
        link_kind='ntfs_directory_junction'
    else:
        linked.symlink_to(outside,target_is_directory=True)
        assert linked.is_symlink()
        link_kind='directory_symlink'
    assert linked.resolve()==outside.resolve() and not linked.resolve().is_relative_to(root.resolve())
    probe_code=r'''
import json,os,runpy,sys
from pathlib import Path
import code_review_graph.incremental as inc
bridge,root,candidate=map(Path,sys.argv[1:])
sys.path.insert(0,str(bridge.parent))
original_binary,original_read=inc._is_binary,Path.read_bytes
counts={'binary_probe_calls':0,'source_read_bytes_calls':0}
def matches(path):
    return os.path.normcase(os.path.abspath(os.fspath(path)))==os.path.normcase(os.path.abspath(os.fspath(candidate)))
def binary_trap(path):
    if matches(path):
        counts['binary_probe_calls']+=1
        raise AssertionError('binary_read_attempt')
    return original_binary(path)
def bytes_trap(path):
    if matches(path):
        counts['source_read_bytes_calls']+=1
        raise AssertionError('source_read_attempt')
    return original_read(path)
inc._is_binary,Path.read_bytes=binary_trap,bytes_trap
namespace=runpy.run_path(str(bridge))
sys.argv=[str(bridge),str(root),'scope']
rejected=False
try:
    namespace['main']()
except RuntimeError as exc:
    rejected=str(exc)=='scope_escape'
except AssertionError:
    pass
print(json.dumps(dict(counts,rejected_before_content_reads=rejected and not any(counts.values()))))
'''
    config=json.loads((cli.parent/'graph-refresh.json').read_text())
    try:
        process=subprocess.run([config['crg_python'],'-E','-B','-c',probe_code,
            str(cli.parent/'graph_crg_bridge.py'),str(root),str(linked/'a.py')],
            cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=60,
            env=dict(os.environ,DO_NOT_TRACK='1',GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1'))
        assert process.returncode==0,'local read-trap probe failed'
        probe=json.loads(process.stdout)
        print(json.dumps({'boundary_read_trap':probe,'link_kind':link_kind}),flush=True)
        assert probe['rejected_before_content_reads'],probe
    finally:
        # These are fixture-owned links, never recursively remove their targets.
        assert linked.resolve()==outside.resolve()
        if os.name=='nt': linked.rmdir()
        else: linked.unlink()
    linked.mkdir()
    (linked/'a.py').write_text('def fixture_boundary_restored():\n    return 2\n',encoding='utf-8')
    (root/'untracked.py').write_text('def fixture_boundary_untracked():\n    return 3\n',encoding='utf-8')
    initial=call(cli,'ensure',root,True)
    query(root,'fixture_boundary_restored');query(root,'fixture_boundary_untracked')
    (root/'untracked.py').write_text('def fixture_boundary_untracked_new():\n    return 4\n',encoding='utf-8')
    stale=call(cli,'status',root,False)
    assert stale['backends']['code-review-graph']['modified']==1,stale
    final=call(cli,'refresh',root,True)
    query(root,'fixture_boundary_untracked_new');query(root,'fixture_boundary_untracked',False)
    return {'link_kind':link_kind,'boundary_read_trap':probe,'local_ingestion':initial,
            'supported_untracked_stale':stale,'final':final,
            'native_query_search':{'real_sqlite_symbols_and_hashes':True}}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--cli',action='append',required=True); p.add_argument('--report',required=True); p.add_argument('--fixture-root'); p.add_argument('--smoke',action='store_true',help='Ingestion lifecycle only; full fault suite is the default'); p.add_argument('--scope-only',action='store_true',help='Targeted native YAML/empty Python/untracked scope contract regression'); p.add_argument('--boundary-only',action='store_true',help='Real directory-link read trap plus local/untracked ingestion regression')
    args=p.parse_args(); report={}
    with tempfile.TemporaryDirectory(prefix='graph-real-',dir=args.fixture_root) as directory:
        for i,cli in enumerate(args.cli):
            cli=Path(cli).resolve(); start=time.monotonic()
            if args.boundary_only:
                result=boundary_contract(cli,Path(directory)/f'r{i}')
                summary='directory-link rejected before binary/source reads; real local/untracked ingestion'
            elif args.scope_only:
                result=scope_contract(cli,Path(directory)/f'r{i}')
                summary='native YAML scope, Spring/Ansible, empty Python, untracked edits and scope transitions'
            else:
                result=exercise(cli,Path(directory)/f'r{i}',faults=not args.smoke)
                summary='real graph ingestion, untracked, rename/delete, preserved mtime, no-change'+('' if args.smoke else ', locks, faults, source mutation')
            report[str(cli)]=result
            print(f'PASS {cli.parent.parent.name}: {summary} ({time.monotonic()-start:.1f}s)',flush=True)
            Path(args.report).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__': main()
