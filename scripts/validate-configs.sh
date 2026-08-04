#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Syntax and structure are checked first; semantic conflicts are evaluated second.
python3 "$repo_root/scripts/validate-rules.py"
python3 "$repo_root/scripts/lint-rules.py"
