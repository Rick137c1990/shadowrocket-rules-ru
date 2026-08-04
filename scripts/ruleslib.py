#!/usr/bin/env python3
"""Shared parser and helpers for Shadowrocket configuration tooling."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import ipaddress
import re

ALLOWED_SECTIONS = {"General", "Rule", "Host", "URL Rewrite"}
DOMAIN_RULES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD"}
IP_RULES = {"IP-CIDR", "IP-CIDR6"}
POLICIES = {"DIRECT", "PROXY", "REJECT"}
RULE_TYPES = DOMAIN_RULES | IP_RULES | {"GEOIP", "FINAL", "AND"}
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*$", re.I)


@dataclass(frozen=True)
class SourceLine:
    path: Path
    number: int
    text: str


@dataclass
class Config:
    path: Path
    metadata: dict[str, str] = field(default_factory=dict)
    metadata_lines: dict[str, SourceLine] = field(default_factory=dict)
    sections: dict[str, list[SourceLine]] = field(default_factory=dict)
    section_order: list[str] = field(default_factory=list)
    repeated_sections: list[SourceLine] = field(default_factory=list)
    unknown_sections: list[SourceLine] = field(default_factory=list)
    orphan_lines: list[SourceLine] = field(default_factory=list)


@dataclass(frozen=True)
class Rule:
    source: SourceLine
    kind: str
    value: str
    policy: str
    options: tuple[str, ...] = ()

    @property
    def identity(self) -> tuple[str, str]:
        return self.kind, self.value.lower()


def parse_config(path: Path) -> Config:
    # Preserve source locations so every diagnostic can point to the original line.
    config = Config(path=path)
    current: str | None = None
    seen_sections: set[str] = set()

    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        text = raw.strip()
        source = SourceLine(path, number, text)
        if not text or text.startswith("#") and not text.startswith("#!"):
            continue
        if text.startswith("#!"):
            payload = text[2:]
            if "=" in payload:
                key, value = payload.split("=", 1)
                config.metadata[key.strip()] = value.strip()
                config.metadata_lines[key.strip()] = source
            else:
                config.orphan_lines.append(source)
            continue
        if text.startswith("[") and text.endswith("]"):
            current = text[1:-1]
            if current not in ALLOWED_SECTIONS:
                config.unknown_sections.append(source)
            if current in seen_sections:
                config.repeated_sections.append(source)
            else:
                seen_sections.add(current)
                config.section_order.append(current)
                config.sections[current] = []
            continue
        if current is None:
            config.orphan_lines.append(source)
        elif current in config.sections:
            config.sections[current].append(source)
    return config


def parse_rule(source: SourceLine) -> Rule | None:
    text = source.text
    kind = text.split(",", 1)[0]
    if kind not in RULE_TYPES:
        return None
    if kind == "AND":
        # AND expressions contain nested commas, so a plain split would corrupt them.
        match = re.fullmatch(r"AND,(\(\(.+\)\)),([^,]+)", text)
        if not match:
            return Rule(source, kind, "", "")
        return Rule(source, kind, match.group(1), match.group(2))
    fields = tuple(part.strip() for part in text.split(","))
    if kind == "FINAL":
        policy = fields[1] if len(fields) > 1 else ""
        return Rule(source, kind, "", policy, fields[2:])
    value = fields[1] if len(fields) > 1 else ""
    policy = fields[2] if len(fields) > 2 else ""
    return Rule(source, kind, value, policy, fields[3:])


def iter_rules(config: Config) -> list[Rule]:
    return [rule for line in config.sections.get("Rule", []) if (rule := parse_rule(line))]


def is_valid_domain(value: str) -> bool:
    if value in {"local", "home.arpa"}:
        return True
    try:
        ascii_value = value.encode("idna").decode("ascii")
    except UnicodeError:
        return False
    return bool(DOMAIN_RE.fullmatch(ascii_value))


def is_valid_network(value: str, version: int) -> bool:
    try:
        return ipaddress.ip_network(value, strict=False).version == version
    except ValueError:
        return False


def config_kind(path: Path) -> str:
    parts = set(path.parts)
    if "builds" in parts:
        return "build"
    if "modules" in parts:
        return "module"
    if "base" in parts:
        return "base"
    if "custom" in parts:
        return "custom"
    return "other"
