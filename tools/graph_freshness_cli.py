#!/usr/bin/env python3
"""Verify/refresh this exact Git root's local AST graphs. Python standard library only."""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import graph_paths as paths
OFFLINE = {'DO_NOT_TRACK': '1', 'CODEGRAPH_NO_UPDATE_CHECK': '1',
           'CODEGRAPH_NO_DOWNLOAD': '1', 'NO_COLOR': '1', 'PYTHONDONTWRITEBYTECODE': '1',
           'CRG_RECURSE_SUBMODULES': '0', 'GIT_OPTIONAL_LOCKS': '0'}


class GraphError(Exception):
    pass


def run(argv, root, payload=None, timeout=600):
    """No shell interpolation. Never expose native stderr/source in errors."""
    try:
        environment = {k:v for k,v in os.environ.items() if k.upper() not in {'PYTHONHOME','PYTHONPATH'}}
        environment.update(OFFLINE)
        result = subprocess.run([str(x) for x in argv], cwd=root,
            env=environment, input=payload, capture_output=True,
            text=True, encoding='utf-8', errors='replace', timeout=timeout,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except (OSError, subprocess.TimeoutExpired):
        raise GraphError('local_process_unavailable_or_timeout') from None
    if result.returncode:
        raise GraphError('local_operation_failed')
    return result.stdout.strip()


def root_path(value):
    root = Path(value).expanduser().resolve(strict=True)
    actual = Path(run(['git', 'rev-parse', '--show-toplevel'], root)).resolve()
    if root != actual:
        raise GraphError('cwd_must_be_exact_git_root')
    return root


def discover(config, root):
    found, unavailable = {}, {}
    try:
        # Volta reports its active installed package, never a fixed npx hash.
        volta = shutil.which('volta')
        command = config.get('codegraph_command') or shutil.which('codegraph')
        if not command:
            raise GraphError('codegraph_not_installed')
        launcher = Path(command)
        candidates = [launcher.parent / 'node_modules/@colbymchenry/codegraph']
        if volta:
            active = Path(run([volta, 'which', 'codegraph'], root, timeout=20))
            candidates.insert(0, active.parent / 'node_modules/@colbymchenry/codegraph')
        if config.get('codegraph_package_root'):
            candidates.insert(0, Path(config['codegraph_package_root']))
        package = next(p for p in candidates if (p/'package.json').is_file())
        version = json.loads((package/'package.json').read_text('utf-8'))['version']
        if version != config['codegraph_version']:
            raise GraphError('unverified_codegraph_version')
        platform = 'win32-x64' if os.name == 'nt' else f'{sys.platform}-x64'
        bundles = [package/f'node_modules/@colbymchenry/codegraph-{platform}', package.parent/f'codegraph-{platform}']
        bundle = next(p for p in bundles if (p/'lib/dist/index.js').is_file())
        node = bundle/('node.exe' if os.name == 'nt' else 'bin/node')
        if not node.is_file():
            raise GraphError('bundled_node_missing')
        found['codegraph'] = [str(node), '--liftoff-only', '--disable-warning=ExperimentalWarning', str(HERE/'graph_cg_bridge.cjs'), str(bundle/'lib/dist')]
    except (GraphError, OSError, ValueError, KeyError, StopIteration):
        unavailable['codegraph'] = 'local_runtime_unavailable_or_unverified'
    interpreter = config.get('crg_python') or sys.executable
    if Path(interpreter).is_file():
        found['code-review-graph'] = [interpreter, '-E', '-B', str(HERE/'graph_crg_bridge.py')]
    else:
        unavailable['code-review-graph'] = 'local_runtime_unavailable_or_unverified'
    return found, unavailable


def bridge(command, root, action, payload=None):
    try:
        value = json.loads(run([*command, str(root), action], root,
                               json.dumps(payload) if payload is not None else None))
        if value.get('ok') is False:
            raise GraphError('local_graph_operation_failed')
        return value
    except ValueError:
        raise GraphError('invalid_local_adapter_output') from None


def ro(path, allowed_root):
    # mode=ro never creates a missing DB and never runs native schema migrations.
    path = paths.sqlite_target(path, allowed_root)
    connection = sqlite3.connect(path.as_uri()+'?mode=ro', uri=True, timeout=2)
    connection.execute('PRAGMA query_only=ON')
    connection.execute('BEGIN')
    return connection


def inspect_graph(name, scope, root):
    path, expected = Path(scope['db']), scope['hashes']
    target = paths.storage(name, root, path)
    result = {'state': 'missing', 'files': 0, 'nodes': 0, 'expected_files': len(expected),
              'excluded_files': scope.get('excluded_files', {}), 'storage_origin': target['origin']}
    if not path.is_file():
        return result
    try:
        with contextlib.closing(ro(path, target['data_root'])) as db:
            if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise sqlite3.DatabaseError('invalid_database')
            result['nodes'] = db.execute('SELECT count(*) FROM nodes').fetchone()[0]
            reasons = []
            error_files = set()
            if name == 'codegraph':
                rows = db.execute('SELECT path, content_hash, errors FROM files').fetchall()
                actual = {str(p).replace('\\','/'): h for p,h,_ in rows}
                metadata = dict(db.execute('SELECT key,value FROM project_metadata'))
                if metadata.get('index_state') != 'complete': reasons.append('incomplete_index')
                if metadata.get('indexed_with_version') != scope['version'] or metadata.get('indexed_with_extraction_version') != str(scope['extraction_version']):
                    reasons.append('index_version_changed')
                if any(e and e != '[]' for _,_,e in rows): reasons.append('parse_or_scope_warnings')
                error_files = {str(p).replace('\\','/') for p,_,e in rows if e and e != '[]'}
                pending = db.execute("SELECT count(*) FROM unresolved_refs WHERE status='pending'").fetchone()[0]
                if pending: reasons.append('pending_resolution')
                inventory = {str(p).replace('\\','/') for p, in db.execute('SELECT DISTINCT file_path FROM nodes')}
            else:
                rows = db.execute("SELECT file_path,file_hash FROM nodes WHERE kind='File'").fetchall()
                actual = {Path(p).resolve().as_posix(): h for p,h in rows}
                metadata = dict(db.execute('SELECT key,value FROM metadata'))
                if metadata.get('schema_version') != '9' or not metadata.get('last_updated') or not metadata.get('last_postprocessed_at'):
                    reasons.append('incomplete_index')
                inventory = {Path(p).resolve().as_posix() for p, in db.execute('SELECT DISTINCT file_path FROM nodes')}
            missing = set(expected)-set(actual)
            removed = set(actual)-set(expected)
            modified = {p for p in set(expected)&set(actual) if expected[p] != actual[p]}
            if missing or removed or modified: reasons.append('source_changed')
            if inventory-set(actual): reasons.append('orphan_file_nodes')
            if not expected: reasons.append('empty_supported_scope')
            elif not result['nodes'] or not actual: reasons.append('empty_graph')
            result.update(state='stale' if reasons else 'fresh', files=len(actual),
                          reasons=reasons, added=len(missing), modified=len(modified), removed=len(removed),
                          _repair=sorted((missing|modified|error_files)&set(expected)))
    except (sqlite3.Error, OSError, ValueError, KeyError):
        result.update(state='invalid', reasons=['unreadable_or_invalid_database'])
    return result


def scopes_and_status(found, root, config):
    scopes, states = {}, {}
    for name, command in found.items():
        try:
            scope = bridge(command, root, 'scope')
            if name == 'code-review-graph' and scope.get('version') != config['crg_version']:
                raise GraphError('unverified_crg_version')
            scopes[name] = scope
            states[name] = inspect_graph(name, scope, root)
        except (GraphError, paths.PathBoundaryError) as exc:
            states[name] = {'state':'unavailable', 'reason':str(exc)}
    return scopes, states


def fingerprint(scopes):
    return hashlib.sha256(json.dumps(scopes, sort_keys=True).encode()).hexdigest()


@contextlib.contextmanager
def advisory_lock(root):
    git = Path(run(['git','rev-parse','--absolute-git-dir'], root)).resolve()
    target = paths.checked_path(git/'graph-freshness.lock', git)
    stream = target.open('a+b')
    locked = False
    try:
        # Windows byte-range locks forbid even reads of the held byte. Inspect
        # length without touching it, then acquire before accessing its content.
        if not os.fstat(stream.fileno()).st_size: stream.write(b'0'); stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
            locked = True
        except OSError:
            raise GraphError('project_refresh_busy') from None
        yield git
    finally:
        if locked:
            stream.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()


def backup(path, git, name, source_root):
    path = paths.sqlite_target(path, source_root)
    if not path.exists(): return
    directory = paths.checked_path(git/'graph-freshness-backups'/f'{time.time_ns()}-{os.getpid()}', git)
    output = paths.sqlite_target(directory/(name+'.db'), git)
    directory.mkdir(parents=True)
    with contextlib.closing(ro(path, source_root)) as source, contextlib.closing(sqlite3.connect(output)) as target:
        source.backup(target)


def execute(args):
    root = root_path(args.cwd)
    config = json.loads((HERE/'graph-refresh.json').read_text('utf-8-sig'))
    found, unavailable = discover(config, root)
    scopes, states = scopes_and_status(found, root, config) if args.action == 'status' else ({}, {})
    if args.require_both:
        for name, reason in unavailable.items(): states[name]={'state':'unavailable','reason':reason}
    if not found and not states: raise GraphError('no_local_graph_backend')
    operations = []
    if args.action != 'status':
        with advisory_lock(root) as git:
            scopes, states = scopes_and_status(found, root, config)
            if args.require_both:
                for name, reason in unavailable.items(): states[name]={'state':'unavailable','reason':reason}
            before = fingerprint(scopes)
            for name, state in states.items():
                if state['state'] == 'fresh': continue
                if state['state'] in {'invalid','unavailable'}:
                    operations.append({'backend':name, 'result':'refused_invalid_or_unavailable'})
                    continue
                if not scopes[name]['hashes']:
                    operations.append({'backend':name, 'result':'empty_supported_scope'})
                    continue
                path = Path(scopes[name]['db'])
                # Reject native lock presence before SDK open/migration as well.
                if name == 'codegraph' and (path.parent/'codegraph.lock').exists():
                    operations.append({'backend':name, 'result':'native_lock_present'})
                    continue
                target = paths.storage(name, root, path)
                backup(path, git, name, target['data_root'])
                if name == 'code-review-graph':
                    backup(Path(target['legacy_db']), git, 'crg-legacy', root)
                action = 'build' if state['state']=='missing' or state.get('nodes',0)==0 or any(x in state.get('reasons',[]) for x in ('incomplete_index','index_version_changed')) else 'refresh'
                try:
                    bridge(found[name], root, action, {'repair':state.get('_repair',[])})
                    operations.append({'backend':name, 'result':action})
                except GraphError as exc:
                    operations.append({'backend':name, 'result':str(exc)})
            after_scopes, states = scopes_and_status(found, root, config)
            if args.require_both:
                for name, reason in unavailable.items(): states[name]={'state':'unavailable','reason':reason}
            if fingerprint(after_scopes) != before:
                for state in states.values():
                    state.update(state='stale', reasons=['source_changed_during_refresh'])
    fresh = bool(states) and all(s['state']=='fresh' for s in states.values())
    failures = [op for op in operations if op['result'] not in {'build','refresh'}]
    if failures: fresh = False
    public = {name:{k:v for k,v in state.items() if not k.startswith('_')} for name,state in states.items()}
    return {'fresh':fresh, 'ok':fresh, 'action':args.action, 'backends':public, 'operations':operations,
            'scope':'exact_git_root', 'subprojects_refreshed':False}, 0 if fresh else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status','ensure','refresh'])
    parser.add_argument('--cwd', required=True, help='Exact existing Git repository root')
    parser.add_argument('--require-both', action='store_true', help='Require both installed graph backends to verify fresh')
    parser.add_argument('--no-subprojects', action='store_true', help='Compatibility flag; never launches separate child-project refreshes')
    parser.add_argument('--json', action='store_true', help='Output is always sanitized JSON')
    args = parser.parse_args()
    try:
        result, code = execute(args)
    except (GraphError, OSError, ValueError, KeyError, RuntimeError, sqlite3.Error) as exc:
        result, code = {'fresh':False, 'ok':False, 'error':str(exc) if isinstance(exc, (GraphError, paths.PathBoundaryError)) else type(exc).__name__}, 2
    print(json.dumps(result, ensure_ascii=True))
    return code


if __name__ == '__main__':
    sys.exit(main())
