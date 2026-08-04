#!/usr/bin/env python3
"""Best-effort DNS health report; intentionally separate from required CI."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import socket
import sys

from ruleslib import iter_rules, parse_config

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "shadowrocket" / "modules"


def collect_domains() -> list[str]:
    domains: set[str] = set()
    for path in sorted(MODULES.glob("*.conf")):
        for rule in iter_rules(parse_config(path)):
            if rule.kind not in {"DOMAIN", "DOMAIN-SUFFIX"}:
                continue
            domain = rule.value.lower().rstrip(".")
            # Country-code suffix rules such as "ru" are routing selectors, not hosts.
            if "." not in domain or domain in {"local", "home.arpa"} or domain.endswith(".example.com"):
                continue
            domains.add(domain)
    return sorted(domains)


def resolve(domain: str, timeout: float) -> dict[str, object]:
    previous = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        canonical, aliases, addresses = socket.gethostbyname_ex(domain)
        return {"domain": domain, "status": "active", "canonical": canonical, "aliases": aliases, "addresses": sorted(set(addresses))}
    except socket.gaierror as exc:
        status = "nxdomain" if exc.errno in {-2, -5, 8} else "dns-error"
        return {"domain": domain, "status": status, "error": str(exc)}
    except TimeoutError as exc:
        return {"domain": domain, "status": "timeout", "error": str(exc)}
    finally:
        socket.setdefaulttimeout(previous)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--timeout", type=float, default=4.0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on-nxdomain", action="store_true")
    args = parser.parse_args()

    domains = collect_domains()
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(resolve, domain, args.timeout): domain for domain in domains}
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: str(item["domain"]))
    summary: dict[str, int] = {}
    for result in results:
        status = str(result["status"])
        summary[status] = summary.get(status, 0) + 1
        if status != "active":
            print(f"{status.upper():9} {result['domain']}: {result.get('error', '')}")
    report = {"summary": summary, "results": results}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Checked {len(results)} domains: {summary}")
    return 1 if args.fail_on_nxdomain and summary.get("nxdomain", 0) else 0


if __name__ == "__main__":
    sys.exit(main())
