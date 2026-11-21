"""Local CRG AST adapter; no MCP, embeddings, model or network entry points."""
from __future__ import annotations
import contextlib
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import subprocess
import sys
import graph_paths as paths


def main():
    root, action = Path(sys.argv[1]).resolve(), sys.argv[2]
    import code_review_graph.incremental as inc
    from code_review_graph.parser import CodeParser, _ansible_file_type, _is_ansible_content
    target = paths.crg_storage(root)
    db = Path(target['db'])
    # Use native language, binary and ignore rules, with git-visible untracked
    # candidates added to the native tracked inventory.
    candidates = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root, capture_output=True, check=True).stdout.decode('utf-8').split('\0')
    parser, patterns = CodeParser(root), inc._load_ignore_patterns(root)
    hashes, excluded, excluded_paths = {}, {}, []
    for rel in sorted(set(candidates)):
        p = root / rel
        if not rel or inc._should_ignore(rel, patterns) or not p.is_file() or p.is_symlink():
            continue
        if not p.resolve().is_relative_to(root):
            raise RuntimeError('scope_escape')
        if inc._is_binary(p):
            continue
        raw = p.read_bytes()
        language = parser.detect_language(p, raw)
        if language is None:
            continue
        # CRG 2.3.8 detect_language recognizes the extension, but parse_bytes
        # deliberately returns no nodes for generic YAML (parser.py:2695).
        # Mirror only that explicit native contract; never infer exclusion from
        # a missing File row or a parser failure. Spring/Ansible stay supported.
        reason = None
        if language == 'yaml':
            reason = 'generic_yaml_not_supported_by_native_parser'
        elif language == 'ansible' and _ansible_file_type(p) not in ('vars', 'meta') and not _is_ansible_content(raw):
            reason = 'ansible_path_without_native_content_evidence'
        if reason:
            excluded[reason] = excluded.get(reason, 0) + 1
            excluded_paths.append(p.resolve().as_posix())
            continue
        hashes[p.resolve().as_posix()] = hashlib.sha256(raw).hexdigest()
    if action == 'scope':
        return {'db': str(db), 'hashes': hashes, 'excluded_files': excluded,
                'storage_origin': target['origin'],
                'version': importlib.metadata.version('code-review-graph')}
    from code_review_graph.graph import GraphStore
    from code_review_graph.tools.build import run_postprocess
    paths.crg_storage(root)  # Before native mkdir/.gitignore/legacy migration.
    native_db = inc.get_db_path(root)
    paths.storage('code-review-graph', root, native_db)
    store = GraphStore(native_db)
    results = []
    try:
        # An existing graph can always reconcile explicit paths, even without HEAD.
        if not store.has_nodes():
            results.append(inc.full_build(root, store, recurse_submodules=False))
        # A formerly supported Ansible file can become generic YAML. Native
        # reconciliation checks detect_language only, so remove precisely those
        # explicitly unsupported paths through its own atomic cleanup API.
        if excluded_paths:
            store.remove_files_permanently(excluded_paths)
        explicit = [str(Path(p).relative_to(root)) for p in hashes]
        results.append(inc.incremental_update(root, store, changed_files=explicit))
        if any(result.get('errors') for result in results):
            raise RuntimeError('parse_failed')
    finally:
        store.close()
    paths.crg_storage(root)  # Postprocess opens the same native DB again.
    post = run_postprocess(repo_root=str(root), flows=True, communities=True, fts=True,
                           embedding_provider=None, embedding_model=None)
    if post.get('warnings') or post.get('status') != 'ok':
        raise RuntimeError('postprocess_incomplete')
    return {'ok': True, 'mode': 'incremental', 'files_updated': sum(r.get('files_updated', r.get('files_parsed', 0)) for r in results)}


if __name__ == '__main__':
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = main()
        print(json.dumps(result))
    except Exception:
        print(json.dumps({'ok': False, 'error': 'local_crg_operation_failed'}))
        sys.exit(1)
