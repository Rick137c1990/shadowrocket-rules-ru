# Installation and project structure

[English](instructions.md) | [Русский](instructions.ru.md)

## Before you start

You need Shadowrocket and a working proxy node or policy named `PROXY`. The
repository provides routing rules, not a proxy server.

## Choose an installation method

### Ready-made profile

Choose `MINIMAL`, `ADVANCED`, or `FULL` in `Shadowrocket/builds`. Open the file on
GitHub, copy its Raw URL, and add it as a remote configuration in Shadowrocket.
The files are generated from the modules and contain no identical duplicate
rules.

### Base plus optional modules

1. Add `Shadowrocket/base/base.conf` as the base configuration.
2. Open `Shadowrocket/catalog/MODULES.md`.
3. Copy the Raw URL of each required module.
4. In Shadowrocket, open **Config > Modules**, add the URL, and enable the module.
5. Review module order and test both DIRECT and PROXY destinations.

To create personal rules, copy
`Shadowrocket/custom/custom.example.conf`, rename it, and follow the
[custom-rules guide](manual.md).

## Validation checklist

- local network resources remain reachable;
- Russian services that require a Russian IP use `DIRECT`;
- selected international services use `PROXY`;
- DNS and IP leak tests show the expected route;
- authentication, banking, media, and messaging apps still work.

Return to the [main README](../README.md).
