#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "$repo_root/scripts/validate-rules.py"
python3 "$repo_root/scripts/lint-rules.py"
