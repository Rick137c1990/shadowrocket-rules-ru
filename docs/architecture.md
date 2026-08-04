# Technical architecture

[Русская версия](architecture.ru.md) · [Main README](../README.md) · [Module guide](modules.md)

This document explains how the repository turns independent Shadowrocket modules into ready-to-use profiles and how the automated checks protect that process.

## Design goals

The project supports two equally important usage modes:

1. **Standalone modules.** A user can import a module into Shadowrocket and enable or disable it with one tap.
2. **Ready-made profiles.** A user who does not want to assemble modules can import `minimal.conf`, `advanced.conf`, or `full.conf`.

For this reason, modules are intentionally self-contained. The same domain may appear in several modules when each module needs it to work independently. Exact duplicates are removed only while ready-made profiles are generated.

## Repository layout

```text
shadowrocket/
├── base/       # Shared General, Rule, and Host settings
├── modules/    # Independently installable feature modules
├── builds/     # Generated ready-made profiles
├── catalog/    # Machine-friendly module catalog
└── custom/     # Example for user-owned rules
scripts/
├── ruleslib.py          # Shared parser and data model
├── build-configs.sh     # Profile generator
├── validate-rules.py    # Structural and syntax validator
├── lint-rules.py        # Semantic conflict and ordering linter
├── validate-configs.sh  # Local validation entry point
└── check-domains.py     # Optional DNS health check
```

## Processing flow

```text
base.conf + selected standalone modules
                  │
                  ▼
          build-configs.sh
                  │
                  ▼
      minimal / advanced / full
                  │
          ┌───────┴────────┐
          ▼                ▼
  validate-rules.py   lint-rules.py
          │                │
          └───────┬────────┘
                  ▼
          GitHub Actions CI
```

`base.conf` contains settings shared by generated profiles. Modules contain only the sections required for their feature and must remain usable on their own. Generated builds are artifacts: edit their sources and run the generator instead of editing a build directly.

## How profile generation works

`scripts/build-configs.sh`:

1. Resolves every path relative to the repository root, so it can be run from any directory.
2. Creates a temporary workspace with `mktemp` and removes it on exit.
3. Selects a documented list of modules for each profile.
4. Extracts `[General]`, `[Rule]`, `[Host]`, and `[URL Rewrite]` content with `awk`.
5. Preserves source comments while removing exact duplicate rule lines from a generated profile.
6. Adds exactly one `FINAL` rule at the end of `[Rule]`.
7. Writes the result to `shadowrocket/builds/`, or to `BUILD_OUTPUT_DIR` when the validator requests an isolated rebuild.

The order of rules is significant because Shadowrocket evaluates rules from top to bottom. A specific exception must therefore appear before the broader rule that would otherwise match it.

## Parser and validator

`scripts/ruleslib.py` is the shared parsing layer. It records paths and line numbers in `SourceLine`, represents a parsed file as `Config`, and normalizes routing entries as `Rule`. Both validation tools use this model so they interpret configuration files consistently.

`scripts/validate-rules.py` checks facts that are unambiguously invalid:

- required metadata and sections;
- unknown or repeated sections;
- content outside sections;
- supported rule types and policies;
- domain names, IPv4/IPv6 CIDR ranges, and rule field counts;
- URL Rewrite regular expressions, targets, and status codes;
- absence of `FINAL` in reusable sources;
- exactly one final-position `FINAL` in generated profiles;
- byte-for-byte synchronization between committed builds and a fresh isolated build.

Validation findings are `ERROR`s and fail the command.

## Semantic linter

`scripts/lint-rules.py` analyzes valid rules whose interaction may still be surprising:

- the same selector with different policies;
- exact duplicate rules;
- a domain hidden by an earlier `DOMAIN-SUFFIX`;
- a specific suffix hidden by an earlier broader suffix;
- risky `DOMAIN-KEYWORD` rules;
- duplicate or overlapping IP networks;
- cross-module overlaps and policy differences;
- rules located after `FINAL`.

Severity has the following meaning:

- `ERROR` — deterministic conflict that can change routing and fails linting;
- `WARNING` — suspicious or overly broad rule that needs review;
- `INFO` — intentional, valid behavior worth making visible.

For example, `DOMAIN,api.example.com,DIRECT` may precede `DOMAIN-SUFFIX,example.com,PROXY` as a deliberate exception. Reversing them makes the exact rule unreachable and is reported as a shadowing problem.

Cross-module duplicates with the same policy are reported as informational because standalone operation is a product requirement, not a defect. The generator removes exact duplicates only in ready-made builds.

## DNS health check

`scripts/check-domains.py` collects concrete `DOMAIN` and `DOMAIN-SUFFIX` values from modules and resolves them concurrently. It reports active names, NXDOMAIN responses, timeouts, DNS errors, canonical names, and resolved addresses. Results can be written as JSON.

This check is separate from required validation because DNS is external and unstable: failures can depend on the resolver, network, geography, or a temporary outage. A DNS result is maintenance evidence, not proof that a service is blocked or that a routing policy is correct.

## Continuous integration

On every push and pull request, `.github/workflows/validate.yml` rebuilds profiles, runs structural validation and semantic linting, and executes:

```bash
git diff --exit-code
```

The final command fails when generated profiles differ from the committed files. This prevents source-module changes from being merged without updating `minimal.conf`, `advanced.conf`, and `full.conf`.

Domain health runs separately because it depends on the network and should not block deterministic configuration checks.

## Safe change workflow

To add or change rules:

1. Edit the relevant standalone module in `shadowrocket/modules/`. Keep it usable independently.
2. Put narrow exceptions before broader domain suffixes or IP ranges.
3. Do not add `FINAL` to a module or `base.conf`.
4. If a new module belongs in a ready-made profile, add it to the corresponding list in `build-configs.sh`.
5. Rebuild and validate:

   ```bash
   ./scripts/build-configs.sh
   ./scripts/validate-configs.sh
   python3 -m unittest discover -s tests -p 'test_*.py' -v
   git diff --check
   ```

6. Review all warnings and informational overlaps. Fix unexpected findings; document intentional ones.
7. Commit source changes and regenerated builds together.

Do not edit files in `shadowrocket/builds/` manually: the next generation run will replace those changes.
