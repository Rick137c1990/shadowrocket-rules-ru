# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-05

### Added

- Independently switchable routing modules for Russian and international services.
- Generated Minimal, Advanced, and Full profiles.
- Human-readable module catalog and custom-rule guides in English and Russian.
- Illustrated Shadowrocket installation guide in English and Russian.
- Deterministic profile generator and generated-file synchronization check.
- Strict configuration validator, semantic rule linter, and unit tests.
- GitHub Actions workflows for validation and optional DNS health reporting.
- Technical architecture documentation in English and Russian.

### Changed

- Normalized repository paths and filenames to Unix-style lowercase kebab-case.
- Kept modules self-contained while deduplicating exact rules in generated profiles.

### Security

- Added prominent notices that the project contains no proxy credentials or
  services and that users are responsible for configuration and legal compliance.

[1.0.0]: https://github.com/Rick137c1990/shadowrocket-rules-ru/releases/tag/v1.0.0
