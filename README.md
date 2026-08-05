# Shadowrocket Rules RU

[English](README.md) | [Русский](README.ru.md)

[![Validate rules](https://github.com/Rick137c1990/shadowrocket-rules-ru/actions/workflows/validate.yml/badge.svg)](https://github.com/Rick137c1990/shadowrocket-rules-ru/actions/workflows/validate.yml)

> **Project status: actively maintained.** The rule set will continue to evolve
> while access restrictions and service infrastructure in Russia keep changing.

Modular routing rules for Shadowrocket, designed for people who connect from
Russia.

## Quick Start

1. Install Shadowrocket and add your own working proxy server.
2. Choose [`minimal.conf`](shadowrocket/builds/minimal.conf),
   [`advanced.conf`](shadowrocket/builds/advanced.conf), or
   [`full.conf`](shadowrocket/builds/full.conf).
3. Open the file on GitHub, tap **Raw**, and copy the URL.
4. Import that URL into Shadowrocket and enable the downloaded configuration.
5. Test both a `DIRECT` destination and a service expected to use `PROXY`.

Prefer switchable features? Keep your existing configuration and follow the
[illustrated module installation guide](docs/instructions.md).

> ### Shadowrocket on the App Store
>
> **Rule-based proxy utility** by Shadow Launch Technology Limited<br>
> Available for Apple platforms. A separate purchase may be required; availability
> and price depend on your App Store region.<br>
> [**View Shadowrocket in the App Store →**](https://apps.apple.com/app/shadowrocket/id932747118)
>
> Shadowrocket is a third-party application and is not affiliated with this project.

## Why this project exists

I created this project for my own daily use. Access restrictions in Russia mean
that some international services need a proxy, while banks, government portals,
marketplaces, and other Russian services often work more reliably with a Russian
IP address. Maintaining every exception by hand on an iPhone quickly becomes
inconvenient.

The project provides two equally supported workflows:

- install a ready-made profile and use it immediately;
- start with the base configuration and enable or disable independent modules in
  Shadowrocket with a single tap.

## What is Shadowrocket?

[Shadowrocket](https://apps.apple.com/app/shadowrocket/id932747118) is a paid
network utility for iOS and iPadOS. It connects to user-provided proxy servers and
routes traffic according to domain, IP, GeoIP, protocol, and rewrite rules.

This repository contains routing rules only. It does **not** provide a proxy
server, VPN subscription, credentials, or network access.

## Choose how to use the project

### Ready-made profiles

| Profile | Default behavior | Intended use |
|---|---|---|
| [`minimal.conf`](shadowrocket/builds/minimal.conf) | Unmatched traffic uses `DIRECT` | Only common social, messaging, and streaming services use `PROXY` |
| [`advanced.conf`](shadowrocket/builds/advanced.conf) | Unmatched traffic uses `PROXY` | Russian services stay direct; other traffic uses the proxy |
| [`full.conf`](shadowrocket/builds/full.conf) | Unmatched traffic uses `PROXY` | Advanced profile plus privacy, crypto, and URL rewrites |

### Independent modules

Every file in [`shadowrocket/modules`](shadowrocket/modules) works independently.
For example, a user can enable AI and developer tools without enabling streaming,
or temporarily disable the social and messaging module with one tap.

Some domains intentionally occur in multiple modules so each module remains
self-contained. The build generator removes identical duplicates from ready-made
profiles.

- [Human-readable module guide](docs/modules.md)
- [Technical architecture](docs/architecture.md)
- [Installation guide](docs/instructions.md)
- [Custom rules and syntax](docs/manual.md)
- [Changelog](CHANGELOG.md)

## Repository layout

```text
shadowrocket/
├── base/                  # common configuration foundation
├── modules/               # independent, switchable modules
├── builds/                # generated minimal, advanced, and full profiles
├── catalog/               # compact module index and Raw URL prefix
└── custom/                # template for personal rules
scripts/
├── build-configs.sh       # deterministic profile generator
├── validate-rules.py      # strict syntax and structure validator
├── lint-rules.py          # semantic conflict and ordering checks
└── check-domains.py       # optional DNS health report
```

## Development checks

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
./scripts/build-configs.sh
./scripts/validate-configs.sh
git diff --exit-code
```

GitHub Actions runs these checks on every push and pull request. A separate
weekly workflow creates a best-effort DNS health report without blocking normal
development.

## Important notice

- You are responsible for your proxy, device configuration, security, and
  compliance with applicable laws and service terms.
- Service availability and domain infrastructure can change without notice.
- A successful DNS check does not mean that a service is accessible from a
  particular network or country.
- These rules do not guarantee anonymity or protection from DNS, WebRTC, IP, or
  application-level leaks.
- Test banking, government, authentication, calling, and payment applications
  before relying on a profile permanently.
- Review third-party configurations before importing them into Shadowrocket.

Use the project at your own risk.

## License

[MIT](LICENSE)
