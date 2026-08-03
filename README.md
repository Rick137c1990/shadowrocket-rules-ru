# Shadowrocket Rules RU

[English](README.md) | [Русский](README.ru.md)

A modular Shadowrocket routing project designed for users in Russia. The goal is
to keep Russian services on a direct connection and route selected international
services through the user's existing `PROXY` policy.

> Always test routing after installation. Service availability and domain
> infrastructure can change over time.

## Project model

- `base/base.conf` contains the common foundation.
- `modules/` contains optional feature and service rule modules.
- `builds/` contains three generated, directly importable configurations.
- `catalog/MODULES.md` lists the available modules and their Raw links.
- `docs/` explains installation, configuration syntax, and custom rules.

## Ready-made profiles

| Profile | Intended use |
|---|---|
| `MINIMAL` | Selected social and streaming services via proxy; other unmatched traffic direct |
| `ADVANCED` | Common Russian services direct; other unmatched traffic through proxy |
| `FULL` | Advanced routing plus privacy, crypto, and URL rewrites |

The profiles are intended for users who do not want to select modules manually.
Advanced users can start with the base configuration and add only the modules
they need.

Modules are intentionally self-contained and may share rules. Generated profiles
are built by `scripts/build-configs.sh`, which removes identical duplicates.

## Documentation

- [Installation and project structure](docs/instructions.md)
- [Shadowrocket syntax and custom rules](docs/manual.md)
- [Module catalog](Shadowrocket/catalog/MODULES.md)

## Requirements

- Shadowrocket for iOS or iPadOS
- an existing proxy node or policy named `PROXY`
- Shadowrocket global routing mode set to use the active configuration

This repository contains routing rules only. It does not provide proxy servers,
VPN access, or anonymity guarantees.

## License

[MIT](LICENSE)
