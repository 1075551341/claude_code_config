"""Small, standard-library guards for graph metadata, never source-file scope."""
from __future__ import annotations
import json
import os
from pathlib import Path
import stat


class PathBoundaryError(ValueError):
    def __init__(self):
        super().__init__('unapproved_graph_metadata_path')


def absolute(path, base):
    value = Path(path).expanduser()
    return Path(os.path.abspath(value if value.is_absolute() else Path(base)/value))


def checked_path(path, allowed_root):
    """Reject existing aliases before any content IO, including missing leaves."""
    try:
        root = Path(allowed_root).resolve()
        candidate = absolute(path, root)
        relative = candidate.relative_to(root)
        current = root
        for part in relative.parts:
            current /= part
            try:
                info = current.lstat()
            except FileNotFoundError:
                continue
            if current.is_symlink() or current.is_junction():
                raise PathBoundaryError()
            # A graph DB/sidecar/lock hardlink can modify an unrelated inode.
            # This guard is called only on managed metadata paths, not sources.
            if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
                raise PathBoundaryError()
        if not candidate.resolve().is_relative_to(root):
            raise PathBoundaryError()
        return candidate
    except (OSError, RuntimeError, ValueError):
        raise PathBoundaryError() from None


def sqlite_target(path, allowed_root):
    target = checked_path(path, allowed_root)
    for suffix in ('-wal', '-shm', '-journal'):
        checked_path(str(target)+suffix, allowed_root)
    return target


def _data_root(raw, repo, explicit):
    lexical = absolute(raw, repo)
    if not explicit or lexical.is_relative_to(repo):
        return checked_path(lexical, repo), repo
    # Only a native-recognized explicitly external config authorizes this root.
    # Its canonical root is allowed; aliases below it remain forbidden.
    try:
        canonical = lexical.resolve()
    except (OSError, RuntimeError):
        raise PathBoundaryError() from None
    return canonical, canonical


def _graph_targets(directory, allowed, filename, origin, lock=False):
    directory = checked_path(directory, allowed)
    checked_path(directory/'.gitignore', directory)
    db = sqlite_target(directory/filename, directory)
    if lock:
        checked_path(directory/'codegraph.lock', directory)
    return {'db':str(db),'data_root':str(directory),'allowed_root':str(allowed),'origin':origin}


def codegraph_storage(repo):
    repo = Path(repo).resolve()
    name = os.environ.get('CODEGRAPH_DIR','').strip()
    if not name or '..' in name or '/' in name or '\\' in name or Path(name).is_absolute():
        name = '.codegraph'
    return _graph_targets(repo/name, repo, 'codegraph.db', 'default' if name=='.codegraph' else 'environment_name', lock=True)


def crg_storage(repo):
    """Mirror CRG2.3.8 priority using existing JSON only, never Registry.mkdir."""
    repo = Path(repo).resolve()
    home_value = os.environ.get('CRG_HOME','').strip()
    home = Path(home_value).expanduser() if home_value else Path.home()/'.code-review-graph'
    registry_home, home_allowed = _data_root(home, repo, explicit=True)
    checked_path(registry_home, home_allowed)
    registry = checked_path(registry_home/'registry.json', registry_home)
    selected, origin = None, 'default'
    if registry.is_file():
        try:
            data = json.loads(registry.read_text('utf-8', errors='replace'))
            entries = data.get('repos',[])
            if isinstance(entries,list):
                for entry in entries:
                    if (isinstance(entry,dict) and entry.get('path')==str(repo)
                            and isinstance(entry.get('data_dir'),str) and entry['data_dir']):
                        selected,origin = entry['data_dir'],'registry'
                        break
        except (ValueError, TypeError, AttributeError):
            pass  # Native Registry treats invalid JSON as no mapping.
    override = os.environ.get('CRG_DATA_DIR','').strip()
    if selected is None and override:
        selected,origin = override,'environment'
    directory, allowed = _data_root(selected if selected is not None else repo/'.code-review-graph', repo, explicit=selected is not None)
    result = _graph_targets(directory, allowed, 'graph.db', origin)
    # Native non-RO get_db_path may migrate this DB and remove these sidecars,
    # including when a registered/environment data directory was selected.
    legacy = sqlite_target(repo/'.code-review-graph.db', repo)
    result['legacy_db'] = str(legacy)
    return result


def storage(name, repo, actual_db=None):
    info = codegraph_storage(repo) if name=='codegraph' else crg_storage(repo)
    if actual_db is not None and absolute(actual_db, repo) != Path(info['db']):
        raise PathBoundaryError()
    return info
