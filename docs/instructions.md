# Installation and project structure

[English](instructions.md) | [Русский](instructions.ru.md)

## Before you start

You need Shadowrocket and a working proxy node or policy named `PROXY`. The
repository provides routing rules, not a proxy server.

## Choose an installation method

### Ready-made profile (planned workflow)

The `Shadowrocket/builds` directory reserves three profiles: `MINIMAL`, `ADVANCED`,
and `FULL`. They are currently development manifests and will become directly
importable configurations after the module review. Do not treat the current
manifest files as production-ready Shadowrocket configurations.

### Base plus optional modules

1. Add `Shadowrocket/base/base.conf` as the base configuration.
2. Open `Shadowrocket/catalog/MODULES.md`.
3. Copy the Raw URL of each required module.
4. In Shadowrocket, open **Config > Modules**, add the URL, and enable the module.
5. Review module order and test both DIRECT and PROXY destinations.

## Validation checklist

- local network resources remain reachable;
- Russian services that require a Russian IP use `DIRECT`;
- selected international services use `PROXY`;
- DNS and IP leak tests show the expected route;
- authentication, banking, media, and messaging apps still work.

Return to the [main README](../README.md).
