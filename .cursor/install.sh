#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for the Claude Code config repository.
# Deploys the repo as ~/.claude (Claude Code reads its config from there) and
# installs the Python test dependencies used by the hook and skill test suites.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Claude Code / the validator resolve config from ~/.claude. Point it at the
# checkout so validate_config.py and the hooks find skills/agents/rules/.codegraph.
if [ "$(readlink -f "$HOME/.claude" 2>/dev/null || true)" != "$REPO_ROOT" ]; then
  rm -rf "$HOME/.claude"
  ln -sfn "$REPO_ROOT" "$HOME/.claude"
fi

# Test dependencies (repo has no lockfile; these back hooks/tests + skill-creator).
python3 -m pip install --user --quiet --upgrade \
  pytest pytest-mock PyHamcrest PyYAML

echo "claude_code_config install complete: ~/.claude -> $REPO_ROOT"
