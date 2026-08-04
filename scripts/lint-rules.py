#!/usr/bin/env python3
"""Semantic linter for ordering, overlap, and policy conflicts."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import ipaddress
from pathlib import Path
import sys

from ruleslib import config_kind, iter_rules, parse_config

ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = ROOT / "shadowrocket"


@dataclass(frozen=True)
class Finding:
    severity: str
    path: Path
    line: int
    message: str

    def render(self) -> str:
        try:
            location = self.path.relative_to(ROOT)
        except ValueError:
            location = self.path
        return f"{self.severity} {location}:{self.line}: {self.message}"


def domain_is_covered(domain: str, suffix: str) -> bool:
    domain = domain.lower().rstrip(".")
    suffix = suffix.lower().rstrip(".")
    return domain == suffix or domain.endswith("." + suffix)


def lint_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    rules = iter_rules(parse_config(path))

    identities: dict[tuple[str, str], list] = defaultdict(list)
    for rule in rules:
        identities[rule.identity].append(rule)
        if rule.kind == "DOMAIN-KEYWORD":
            findings.append(Finding("WARNING", path, rule.source.number, f"DOMAIN-KEYWORD {rule.value!r} may match unrelated hosts"))

    for identity, matches in identities.items():
        policies = {rule.policy for rule in matches}
        if len(policies) > 1:
            line = matches[-1].source.number
            findings.append(Finding("ERROR", path, line, f"{identity[0]} {identity[1]!r} uses conflicting policies {sorted(policies)}"))
        elif len(matches) > 1:
            findings.append(Finding("WARNING", path, matches[-1].source.number, f"duplicate rule for {identity[1]!r}"))

    # Shadowrocket uses first-match semantics; an earlier broad suffix can hide exceptions.
    suffixes = [(index, rule) for index, rule in enumerate(rules) if rule.kind == "DOMAIN-SUFFIX"]
    exact_domains = [(index, rule) for index, rule in enumerate(rules) if rule.kind == "DOMAIN"]
    for domain_index, domain_rule in exact_domains:
        for suffix_index, suffix_rule in suffixes:
            if not domain_is_covered(domain_rule.value, suffix_rule.value):
                continue
            if suffix_index < domain_index:
                severity = "ERROR" if domain_rule.policy != suffix_rule.policy else "WARNING"
                message = (
                    f"DOMAIN {domain_rule.value!r} is shadowed by earlier DOMAIN-SUFFIX "
                    f"{suffix_rule.value!r} using {suffix_rule.policy}"
                )
                findings.append(Finding(severity, path, domain_rule.source.number, message))
            elif suffix_rule.policy != domain_rule.policy:
                findings.append(Finding("INFO", path, domain_rule.source.number, f"ordered exception: DOMAIN {domain_rule.value!r} uses {domain_rule.policy} before suffix {suffix_rule.value!r} uses {suffix_rule.policy}"))

    for narrow_index, narrow_rule in suffixes:
        for broad_index, broad_rule in suffixes:
            if narrow_index == broad_index or not domain_is_covered(narrow_rule.value, broad_rule.value):
                continue
            if narrow_rule.value.lower() == broad_rule.value.lower():
                continue
            if broad_index < narrow_index:
                severity = "ERROR" if narrow_rule.policy != broad_rule.policy else "WARNING"
                findings.append(Finding(severity, path, narrow_rule.source.number, f"DOMAIN-SUFFIX {narrow_rule.value!r} is shadowed by earlier broader suffix {broad_rule.value!r} using {broad_rule.policy}"))
            elif broad_rule.policy != narrow_rule.policy:
                findings.append(Finding("INFO", path, narrow_rule.source.number, f"ordered suffix exception: {narrow_rule.value!r} uses {narrow_rule.policy} before {broad_rule.value!r} uses {broad_rule.policy}"))

    networks = []
    for index, rule in enumerate(rules):
        if rule.kind not in {"IP-CIDR", "IP-CIDR6"}:
            continue
        try:
            network = ipaddress.ip_network(rule.value, strict=False)
        except ValueError:
            continue
        networks.append((index, rule, network))
    for left_index, left_rule, left_network in networks:
        for right_index, right_rule, right_network in networks:
            if right_index <= left_index or left_network.version != right_network.version:
                continue
            if left_network == right_network:
                severity = "ERROR" if left_rule.policy != right_rule.policy else "WARNING"
                findings.append(Finding(severity, path, right_rule.source.number, f"duplicate IP range {right_network} with policies {left_rule.policy}/{right_rule.policy}"))
            elif left_network.overlaps(right_network) and left_rule.policy != right_rule.policy:
                findings.append(Finding("ERROR", path, right_rule.source.number, f"overlapping IP ranges {left_network} ({left_rule.policy}) and {right_network} ({right_rule.policy})"))

    final_seen = False
    for rule in rules:
        if final_seen:
            findings.append(Finding("ERROR", path, rule.source.number, "rule appears after FINAL"))
        if rule.kind == "FINAL":
            final_seen = True
    return findings


def lint_across_modules(paths: list[Path]) -> list[Finding]:
    # Same-policy overlap is expected because every module must remain standalone.
    findings: list[Finding] = []
    occurrences: dict[tuple[str, str], list] = defaultdict(list)
    for path in paths:
        for rule in iter_rules(parse_config(path)):
            occurrences[rule.identity].append((path, rule))
    for identity, matches in sorted(occurrences.items()):
        module_paths = {path for path, _ in matches}
        if len(module_paths) < 2:
            continue
        policies = {rule.policy for _, rule in matches}
        path, rule = matches[-1]
        names = ", ".join(sorted(item.name for item in module_paths))
        if len(policies) > 1:
            findings.append(Finding("WARNING", path, rule.source.number, f"cross-module policy conflict for {identity[1]!r}: {sorted(policies)} in {names}"))
        else:
            findings.append(Finding("INFO", path, rule.source.number, f"intentional self-contained overlap for {identity[1]!r} in {names}"))
    return findings


def main() -> int:
    paths = sorted(
        list((CONFIG_ROOT / "base").glob("*.conf"))
        + list((CONFIG_ROOT / "modules").glob("*.conf"))
        + list((CONFIG_ROOT / "builds").glob("*.conf"))
    )
    findings = [finding for path in paths for finding in lint_file(path)]
    module_paths = [path for path in paths if config_kind(path) == "module"]
    findings.extend(lint_across_modules(module_paths))
    rank = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    findings.sort(key=lambda item: (rank[item.severity], str(item.path), item.line, item.message))
    for finding in findings:
        print(finding.render())
    counts = {severity: sum(item.severity == severity for item in findings) for severity in rank}
    print(f"Linted {len(paths)} files: {counts['ERROR']} error(s), {counts['WARNING']} warning(s), {counts['INFO']} info")
    return 1 if counts["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
