'use strict';
// Runs only the installed local SDK. No installer, daemon, MCP or telemetry entry.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const [dist, suppliedRoot, action] = process.argv.slice(2);
const originalWrite = process.stdout.write.bind(process.stdout);
process.stdout.write = () => true; // Native progress can contain private paths/source.
function emit(value) { originalWrite(JSON.stringify(value) + '\n'); }
function checkedMetadata(target, allowedRoot) {
  const base = fs.realpathSync(allowedRoot);
  const candidate = path.resolve(target);
  const relative = path.relative(base, candidate);
  if (relative === '..' || relative.startsWith('..' + path.sep) || path.isAbsolute(relative)) throw Error('metadata_boundary');
  let current = base;
  for (const part of relative.split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    let info;
    try { info = fs.lstatSync(current); }
    catch (e) { if (e.code === 'ENOENT') continue; throw e; }
    if (info.isSymbolicLink() || (info.isFile() && info.nlink !== 1)) throw Error('metadata_alias');
  }
  return candidate;
}
function checkedGraphTargets(db, root) {
  const directory = checkedMetadata(path.dirname(db), root);
  // Use the existing repository root while a missing directory has no realpath.
  for (const leaf of ['.gitignore', path.basename(db), ...['-wal','-shm','-journal'].map(s => path.basename(db)+s), 'codegraph.lock']) {
    checkedMetadata(path.join(directory, leaf), root);
  }
}
async function main() {
  const root = fs.realpathSync(suppliedRoot);
  const {getDatabasePath} = require(path.join(dist, 'db/index.js'));
  const db = getDatabasePath(root);
  checkedGraphTargets(db, root); // Before scope/read, repair, open/init or SQLite.
  const extraction = require(path.join(dist, 'extraction/index.js'));
  if (action === 'scope') {
    const files = (await extraction.scanDirectoryAsync(root)).filter(p => {
      const target = path.resolve(root, p);
      if (!fs.existsSync(target)) return false;
      const relative = path.relative(fs.realpathSync(root), fs.realpathSync(target));
      if (relative === '..' || relative.startsWith('..' + path.sep) || path.isAbsolute(relative)) throw Error('scope_escape');
      return fs.statSync(target).isFile();
    });
    const hashes = {};
    for (const p of files) {
      hashes[p.replaceAll('\\', '/')] = crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p), 'utf8')).digest('hex');
    }
    const {EXTRACTION_VERSION} = require(path.join(dist, 'extraction/extraction-version.js'));
    const {CodeGraphPackageVersion} = require(path.join(dist, 'mcp/version.js'));
    emit({db: getDatabasePath(root), hashes, version: CodeGraphPackageVersion, extraction_version: EXTRACTION_VERSION});
    return;
  }
  const {default: CodeGraph} = require(path.join(dist, 'index.js'));
  const directory = require(path.join(dist, 'directory.js'));
  if (directory.unsafeIndexRootReason(root)) throw Error('unsafe_root');
  const lock = path.join(path.dirname(getDatabasePath(root)), 'codegraph.lock');
  // Never let native stale-lock recovery steal another process's lock.
  if (fs.existsSync(lock)) throw Error('native_lock_present');
  let cg;
  try {
    checkedGraphTargets(db, root);
    cg = fs.existsSync(getDatabasePath(root)) ? await CodeGraph.open(root) : await CodeGraph.init(root, {index: false});
    let result;
    if (action === 'build') result = await cg.indexAll();
    else {
      result = await cg.sync();
      const input = JSON.parse(fs.readFileSync(0, 'utf8') || '{}');
      // Explicit indexFiles bypasses sync's size+mtime shortcut; preserves DB.
      if (input.repair && input.repair.length) {
        // SDK indexFiles expects grammars preloaded, whereas sync only loads
        // languages selected AFTER its stat prefilter. Load repair languages.
        const {loadExtensionOverrides} = require(path.join(dist, 'project-config.js'));
        const overrides = loadExtensionOverrides(root);
        const languages = input.repair.map(p => extraction.detectLanguage(p, fs.readFileSync(path.join(root, p), 'utf8'), overrides));
        if (languages.includes('c')) languages.push('cpp');
        await extraction.loadGrammarsForLanguages(languages);
        const repaired = await cg.indexFiles(input.repair);
        if (!repaired.success || repaired.filesErrored || repaired.errors?.some(x => x.severity === 'error')) throw Error('parse_failed');
        await cg.sync();
      }
    }
    if (result.success === false || result.filesErrored || result.errors?.some(x => x.severity === 'error')) throw Error('parse_failed');
    emit({ok: true, mode: action});
  } finally { if (cg) cg.destroy(); }
}
main().catch(() => { emit({ok: false, error: 'local_codegraph_operation_failed'}); process.exitCode = 1; });
