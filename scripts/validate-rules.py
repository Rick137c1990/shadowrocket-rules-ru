#!/usr/bin/env python3
"""Strict structural and syntax validation for project configurations."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlparse

from ruleslib import (
    ALLOWED_SECTIONS,
    DOMAIN_RULES,
    IP_RULES,
    POLICIES,
    config_kind,
    is_valid_domain,
    is_valid_network,
    iter_rules,
    parse_config,
    parse_rule,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = ROOT / "shadowrocket"
REWRITE_CODES = {"301", "302", "307", "308"}


def error(path: Path, line: int | None, message: str) -> str:
    try:
        location = str(path.relative_to(ROOT))
    except ValueError:
        location = str(path)
    if line is not None:
        location += f":{line}"
    return f"ERROR {location}: {message}"


def config_paths() -> list[Path]:
    return sorted(
        list((CONFIG_ROOT / "base").glob("*.conf"))
        + list((CONFIG_ROOT / "modules").glob("*.conf"))
        + list((CONFIG_ROOT / "builds").glob("*.conf"))
        + list((CONFIG_ROOT / "custom").glob("*.conf"))
    )


def validate_rewrite(text: str) -> str | None:
    fields = text.split()
    if len(fields) != 3:
        return "URL Rewrite must contain a pattern, target URL, and status code"
    pattern, target, status = fields
    try:
        re.compile(pattern)
    except re.error as exc:
        return f"invalid URL Rewrite regular expression: {exc}"
    parsed = urlparse(target)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return "URL Rewrite target must be an absolute HTTP(S) URL"
    if status not in REWRITE_CODES:
        return f"unsupported URL Rewrite status {status}"
    return None


def validate_file(path: Path) -> list[str]:
    issues: list[str] = []
    kind = config_kind(path)
    config = parse_config(path)

    if not path.read_bytes():
        return [error(path, None, "file is empty")]
    for key in ("name", "desc"):
        if not config.metadata.get(key):
            issues.append(error(path, None, f"missing required #!{key} metadata"))
    for section in config.unknown_sections:
        issues.append(error(path, section.number, f"unknown section {section.text}"))
    for section in config.repeated_sections:
        issues.append(error(path, section.number, f"repeated section {section.text}"))
    for line in config.orphan_lines:
        issues.append(error(path, line.number, "content outside a known section"))

    required = {"Rule"}
    if kind in {"base", "build"}:
        required |= {"General", "Host"}
    if kind == "module" and "URL Rewrite" in config.sections:
        required.discard("Rule")
    for section in sorted(required - config.sections.keys()):
        issues.append(error(path, None, f"missing required [{section}] section"))
    if kind == "module":
        for forbidden in {"General", "Host"} & config.sections.keys():
            issues.append(error(path, None, f"module must not contain [{forbidden}]") )

    for line in config.sections.get("General", []):
        if "=" not in line.text:
            issues.append(error(path, line.number, "[General] entry must use key = value"))
    for line in config.sections.get("Host", []):
        if "=" not in line.text:
            issues.append(error(path, line.number, "[Host] entry must use host = value"))
    for line in config.sections.get("URL Rewrite", []):
        if message := validate_rewrite(line.text):
            issues.append(error(path, line.number, message))

    raw_rule_lines = config.sections.get("Rule", [])
    parsed_rules = []
    for line in raw_rule_lines:
        rule = parse_rule(line)
        if rule is None:
            issues.append(error(path, line.number, f"unknown rule type {line.text.split(',', 1)[0]}"))
            continue
        parsed_rules.append(rule)
        if rule.policy not in POLICIES:
            issues.append(error(path, line.number, f"unsupported policy {rule.policy!r}"))
        if rule.kind in DOMAIN_RULES:
            expected = 3
            if len(line.text.split(",")) != expected:
                issues.append(error(path, line.number, f"{rule.kind} requires exactly {expected} fields"))
            if rule.kind != "DOMAIN-KEYWORD" and not is_valid_domain(rule.value):
                issues.append(error(path, line.number, f"invalid domain {rule.value!r}"))
            if rule.kind == "DOMAIN-KEYWORD" and not rule.value:
                issues.append(error(path, line.number, "DOMAIN-KEYWORD value must not be empty"))
        elif rule.kind in IP_RULES:
            if len(line.text.split(",")) not in {3, 4}:
                issues.append(error(path, line.number, f"{rule.kind} requires 3 or 4 fields"))
            version = 4 if rule.kind == "IP-CIDR" else 6
            if not is_valid_network(rule.value, version):
                issues.append(error(path, line.number, f"invalid IPv{version} network {rule.value!r}"))
            if rule.options and rule.options != ("no-resolve",):
                issues.append(error(path, line.number, f"unsupported options {rule.options}"))
        elif rule.kind == "GEOIP":
            if not re.fullmatch(r"[A-Z]{2}", rule.value):
                issues.append(error(path, line.number, "GEOIP value must be a two-letter uppercase code"))
        elif rule.kind == "FINAL" and len(line.text.split(",")) != 2:
            issues.append(error(path, line.number, "FINAL requires exactly two fields"))
        elif rule.kind == "AND" and (not rule.value or not rule.policy):
            issues.append(error(path, line.number, "malformed AND rule"))

    final_indexes = [index for index, rule in enumerate(parsed_rules) if rule.kind == "FINAL"]
    if kind == "build":
        if len(final_indexes) != 1:
            issues.append(error(path, None, "generated build must contain exactly one FINAL rule"))
        elif final_indexes[0] != len(parsed_rules) - 1:
            issues.append(error(path, parsed_rules[final_indexes[0]].source.number, "rules found after FINAL"))
    elif final_indexes:
        issues.append(error(path, parsed_rules[final_indexes[0]].source.number, f"{kind} files must not contain FINAL"))
    return issues


def validate_generated_sync() -> list[str]:
    issues: list[str] = []
    with tempfile.TemporaryDirectory(prefix="shadowrocket-builds-") as temp_dir:
        output = Path(temp_dir)
        subprocess.run(
            [str(ROOT / "scripts" / "build-configs.sh")],
            check=True,
            cwd=ROOT,
            env={**os.environ, "BUILD_OUTPUT_DIR": str(output)},
            stdout=subprocess.DEVNULL,
        )
        expected_names = {"minimal.conf", "advanced.conf", "full.conf"}
        actual_names = {path.name for path in (CONFIG_ROOT / "builds").glob("*.conf")}
        if actual_names != expected_names:
            issues.append(error(CONFIG_ROOT / "builds", None, f"expected builds {sorted(expected_names)}, found {sorted(actual_names)}"))
        for name in expected_names:
            committed = CONFIG_ROOT / "builds" / name
            generated = output / name
            if committed.exists() and generated.exists() and committed.read_bytes() != generated.read_bytes():
                issues.append(error(committed, None, "generated build is out of sync; run scripts/build-configs.sh"))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-generated-sync", action="store_true")
    args = parser.parse_args()
    issues = [issue for path in config_paths() for issue in validate_file(path)]
    if not args.skip_generated_sync:
        issues.extend(validate_generated_sync())
    if issues:
        print("\n".join(issues))
        print(f"Validation failed with {len(issues)} error(s)")
        return 1
    print(f"Validated {len(config_paths())} configuration files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
