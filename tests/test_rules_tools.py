#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load_script(name: str):
    script_path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = load_script("validate-rules.py")
linter = load_script("lint-rules.py")


class RuleToolsTest(unittest.TestCase):
    def fixture(self, directory: Path, content: str) -> Path:
        modules = directory / "modules"
        modules.mkdir(parents=True, exist_ok=True)
        path = modules / "fixture.conf"
        path.write_text(content, encoding="utf-8")
        return path

    def build_fixture(self, directory: Path, content: str) -> Path:
        builds = directory / "builds"
        builds.mkdir(parents=True, exist_ok=True)
        path = builds / "fixture.conf"
        path.write_text(content, encoding="utf-8")
        return path

    def test_valid_standalone_module(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.fixture(Path(temp), """#!name=Test
#!desc=Test module
[Rule]
DOMAIN-SUFFIX,example.com,PROXY
IP-CIDR,203.0.113.0/24,PROXY,no-resolve
""")
            self.assertEqual([], validator.validate_file(path))

    def test_validator_rejects_bad_section_domain_cidr_and_policy(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.fixture(Path(temp), """#!name=Bad
#!desc=Bad module
[Unknown]
value
[Rule]
DOMAIN,bad_domain,UNKNOWN
IP-CIDR,999.1.1.1/24,PROXY
FINAL,PROXY
""")
            messages = "\n".join(validator.validate_file(path))
            self.assertIn("unknown section", messages)
            self.assertIn("invalid domain", messages)
            self.assertIn("invalid IPv4 network", messages)
            self.assertIn("unsupported policy", messages)
            self.assertIn("must not contain FINAL", messages)

    def test_linter_detects_conflicting_domain_policy(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.fixture(Path(temp), """#!name=Conflict
#!desc=Conflict module
[Rule]
DOMAIN,example.com,DIRECT
DOMAIN,example.com,PROXY
""")
            findings = linter.lint_file(path)
            self.assertTrue(any(item.severity == "ERROR" and "conflicting policies" in item.message for item in findings))

    def test_linter_detects_suffix_shadowing(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.fixture(Path(temp), """#!name=Shadow
#!desc=Shadow module
[Rule]
DOMAIN-SUFFIX,example.com,DIRECT
DOMAIN,api.example.com,PROXY
""")
            findings = linter.lint_file(path)
            self.assertTrue(any(item.severity == "ERROR" and "shadowed" in item.message for item in findings))

    def test_linter_warns_about_keyword(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.fixture(Path(temp), """#!name=Keyword
#!desc=Keyword module
[Rule]
DOMAIN-KEYWORD,google,PROXY
""")
            findings = linter.lint_file(path)
            self.assertTrue(any(item.severity == "WARNING" and "unrelated hosts" in item.message for item in findings))

    def test_validator_rejects_repeated_section_and_bad_rewrite(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.fixture(Path(temp), """#!name=Rewrite
#!desc=Rewrite module
[URL Rewrite]
(unclosed https://example.com 999
[URL Rewrite]
^https://example\\.org https://example.com 302
""")
            messages = "\n".join(validator.validate_file(path))
            self.assertIn("repeated section", messages)
            self.assertIn("invalid URL Rewrite regular expression", messages)

    def test_validator_and_linter_reject_rules_after_final(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.build_fixture(Path(temp), """#!name=Build
#!desc=Generated build
[General]
dns-server = system
[Rule]
FINAL,PROXY
DOMAIN,example.com,DIRECT
[Host]
localhost = 127.0.0.1
""")
            messages = "\n".join(validator.validate_file(path))
            self.assertIn("rules found after FINAL", messages)
            self.assertTrue(any(item.severity == "ERROR" and "after FINAL" in item.message for item in linter.lint_file(path)))

    def test_linter_detects_overlapping_ip_policies(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.fixture(Path(temp), """#!name=Networks
#!desc=Network overlap
[Rule]
IP-CIDR,203.0.113.0/24,DIRECT,no-resolve
IP-CIDR,203.0.113.0/25,REJECT,no-resolve
""")
            findings = linter.lint_file(path)
            self.assertTrue(any(item.severity == "ERROR" and "overlapping IP ranges" in item.message for item in findings))


if __name__ == "__main__":
    unittest.main()
