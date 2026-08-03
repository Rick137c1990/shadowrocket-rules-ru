#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
status=0

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  status=1
}

for file in "$repo_root"/Shadowrocket/base/*.conf \
            "$repo_root"/Shadowrocket/modules/*.conf \
            "$repo_root"/Shadowrocket/builds/*.conf; do
  [[ -s "$file" ]] || fail "$file is empty"
  grep -q '^#!name=' "$file" || fail "$file has no #!name metadata"

  awk -F, -v file="$file" '
    /^(DOMAIN|DOMAIN-SUFFIX|DOMAIN-KEYWORD|IP-CIDR|IP-CIDR6|GEOIP),/ {
      if (NF < 3) {
        printf "ERROR: malformed rule at %s:%d: %s\n", file, NR, $0 > "/dev/stderr"
        bad=1
      }
    }
    END { exit bad }
  ' "$file" || status=1
done

for build in "$repo_root"/Shadowrocket/builds/*.conf; do
  final_count="$(grep -c '^FINAL,' "$build" || true)"
  [[ "$final_count" == 1 ]] || fail "$build must contain exactly one FINAL rule"

  duplicates="$(awk '
    /^(DOMAIN|DOMAIN-SUFFIX|DOMAIN-KEYWORD|IP-CIDR|IP-CIDR6|GEOIP|AND|FINAL),/ {
      if (seen[$0]++) print $0
    }
  ' "$build")"
  [[ -z "$duplicates" ]] || fail "$build contains duplicate rules: $duplicates"
done

if [[ "$status" == 0 ]]; then
  printf 'All Shadowrocket configurations passed validation\n'
fi

exit "$status"
