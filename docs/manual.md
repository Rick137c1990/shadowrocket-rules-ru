# Shadowrocket syntax and custom rules

[English](manual.md) | [Русский](manual.ru.md)

This guide covers the syntax used by this project. Keep custom rules in a
separate module so upstream updates do not overwrite them.

## Minimal custom module

```ini
#!name=My Custom Rules
#!desc=Personal routing exceptions

[Rule]
DOMAIN,example.org,PROXY
DOMAIN-SUFFIX,example.com,PROXY
IP-CIDR,203.0.113.0/24,PROXY,no-resolve
```

## Common rule types

| Rule | Matches | Example |
|---|---|---|
| `DOMAIN` | One exact hostname | `DOMAIN,api.example.com,PROXY` |
| `DOMAIN-SUFFIX` | A domain and its subdomains | `DOMAIN-SUFFIX,example.com,PROXY` |
| `DOMAIN-KEYWORD` | Hostnames containing text | `DOMAIN-KEYWORD,example,PROXY` |
| `IP-CIDR` | An IPv4 network | `IP-CIDR,203.0.113.0/24,DIRECT,no-resolve` |
| `IP-CIDR6` | An IPv6 network | `IP-CIDR6,2001:db8::/32,DIRECT,no-resolve` |
| `GEOIP` | IP addresses assigned to a country | `GEOIP,RU,DIRECT` |
| `FINAL` | Traffic not matched earlier | `FINAL,PROXY` |

## Actions

- `DIRECT` connects without the proxy.
- `PROXY` uses the policy named `PROXY`.
- `REJECT` blocks the request.

Rules are evaluated in order. Put narrow exceptions before broad suffix,
country, and final rules. Use `FINAL` only once, at the end of the complete
configuration—not in an optional module.

## Create your own module

1. Copy the minimal template above into a new `.conf` file.
2. Give it a unique `#!name`.
3. Add only the rules you understand and need.
4. Save or host the file as plain text.
5. Add it in **Shadowrocket > Config > Modules**.
6. Test each domain before expanding the rule set.

Do not add credentials, proxy URLs, private keys, or subscription tokens to a
public repository.

Return to the [main README](../README.md).
