#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
base_file="$repo_root/Shadowrocket/base/base.conf"
modules_dir="$repo_root/Shadowrocket/modules"
builds_dir="$repo_root/Shadowrocket/builds"
build_tmp="$(mktemp -d)"
trap 'rm -rf "$build_tmp"' EXIT

extract_section() {
  local file="$1"
  local section="$2"
  awk -v wanted="[$section]" '
    /^\[/ { active = ($0 == wanted); next }
    active { print }
  ' "$file"
}

append_rules() {
  local output="$1"
  local file="$2"
  local label="$3"
  printf '\n# Source: %s\n' "$label" >> "$output"
  extract_section "$file" Rule >> "$output"
}

generate_build() {
  local build_name="$1"
  local final_action="$2"
  shift 2

  local output="$builds_dir/$build_name.conf"
  local rule_source="$build_tmp/$build_name.rules"
  local rewrite_source="$build_tmp/$build_name.rewrites"
  : > "$rule_source"
  : > "$rewrite_source"

  append_rules "$rule_source" "$base_file" "base/base.conf"

  local module
  for module in "$@"; do
    append_rules "$rule_source" "$modules_dir/$module" "modules/$module"
    if grep -q '^\[URL Rewrite\]$' "$modules_dir/$module"; then
      extract_section "$modules_dir/$module" "URL Rewrite" >> "$rewrite_source"
    fi
  done

  {
    printf '#!name=Shadowrocket Rules RU %s\n' "$build_name"
    printf '#!desc=Generated profile. Do not edit; use scripts/build-configs.sh\n\n'
    printf '[General]\n'
    extract_section "$base_file" General
    printf '\n[Rule]\n'
    awk '
      /^[[:space:]]*$/ { if (!blank) print; blank=1; next }
      /^#/ { print; blank=0; next }
      !seen[$0]++ { print; blank=0 }
    ' "$rule_source"
    printf '\nFINAL,%s\n' "$final_action"
    printf '\n[Host]\n'
    extract_section "$base_file" Host
    if [[ -s "$rewrite_source" ]]; then
      printf '\n[URL Rewrite]\n'
      awk 'NF && !seen[$0]++' "$rewrite_source"
    fi
  } > "$output"
}

# MINIMAL proxies only commonly restricted communication and media services.
generate_build MINIMAL DIRECT \
  30_social_messaging.conf \
  50_streaming.conf \
  20_russian_services.conf \
  10_geo_ru.conf

# ADVANCED uses the proxy by default while preserving Russian services directly.
generate_build ADVANCED PROXY \
  30_social_messaging.conf \
  40_ai_developer.conf \
  50_streaming.conf \
  20_russian_services.conf \
  25_vk_group.conf \
  26_yandex_group.conf \
  10_geo_ru.conf

# FULL adds privacy, security, crypto, and optional URL rewrites.
generate_build FULL PROXY \
  30_social_messaging.conf \
  40_ai_developer.conf \
  50_streaming.conf \
  60_privacy_crypto.conf \
  20_russian_services.conf \
  25_vk_group.conf \
  26_yandex_group.conf \
  10_geo_ru.conf \
  90_rewriters.conf

printf 'Generated MINIMAL.conf, ADVANCED.conf, and FULL.conf\n'
