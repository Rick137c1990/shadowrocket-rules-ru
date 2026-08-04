# Module guide

[English](modules.md) | [Русский](modules.ru.md)

Each module is a complete Shadowrocket module that can be installed, enabled, or
disabled independently. Modules never contain `FINAL` and do not depend on other
optional modules.

## Quick choice

| You need | Enable |
|---|---|
| Russian domains and IP ranges directly | `10-geo-ru.conf` |
| Banks, government, telecom, marketplaces, and Russian media directly | `20-russian-services.conf` |
| VK, Mail.ru, OK, and MAX directly | `25-vk.conf` |
| Yandex services directly | `26-yandex.conf` |
| Telegram, WhatsApp, Discord, Instagram, and other social services via proxy | `30-social-messaging.conf` |
| ChatGPT, Claude, Gemini, GitHub, and developer services via proxy | `40-ai-developer.conf` |
| YouTube, Netflix, Spotify, Twitch, and other streaming via proxy | `50-streaming.conf` |
| Privacy, security, VPN, and crypto services via proxy | `60-privacy-crypto.conf` |
| Google China URL redirects | `90-rewriters.conf` |
| Troubleshooting QUIC/HTTP3 routing | `95-disable-quic.conf` |

Raw URL prefix:

```text
https://raw.githubusercontent.com/Rick137c1990/shadowrocket-rules-ru/main/shadowrocket/modules/
```

## `10-geo-ru.conf` — Geo RU Direct

- **Policy:** `DIRECT`
- **Profiles:** minimal, advanced, full
- **Purpose:** sends `.ru`, `.su`, `.рф`, and Russian GeoIP ranges directly.
- **Use it when:** most Russian destinations should bypass the proxy.
- **Caution:** broad country rules must come after narrow `PROXY` exceptions.

## `20-russian-services.conf` — Russian Services Direct

- **Policy:** `DIRECT`
- **Profiles:** minimal, advanced, full
- **Purpose:** government portals, banks, payments, marketplaces, telecom,
  transport, education, and Russian streaming services.
- **Use it when:** these services require a Russian IP or behave poorly through a
  foreign proxy.
- **Caution:** service infrastructure changes; test authentication and payments.

## `25-vk.conf` — VK Ecosystem Direct

- **Policy:** `DIRECT`
- **Profiles:** advanced, full
- **Purpose:** VK, Mail.ru, Odnoklassniki, MAX, authentication, and CDN domains.
- **Use it when:** the whole VK ecosystem should consistently use a direct route.
- **Overlap:** some domains can already match Geo RU; explicit entries also cover
  international infrastructure and keep the module useful on its own.

## `26-yandex.conf` — Yandex Ecosystem Direct

- **Policy:** `DIRECT`
- **Profiles:** advanced, full
- **Purpose:** Yandex core domains, cloud, CDN, regional services, Kinopoisk,
  Auto.ru, Edadeal, and Dzen.
- **Use it when:** Yandex logins, media, maps, or cloud services should not switch
  between proxy and direct routes.
- **Caution:** the module deliberately includes non-`.ru` infrastructure.

## `30-social-messaging.conf` — Social and Messaging Proxy

- **Policy:** `PROXY`
- **Profiles:** minimal, advanced, full
- **Purpose:** Telegram, WhatsApp, Meta platforms, X, Discord, TikTok, Viber,
  Signal, Snapchat, LinkedIn, and Google Meet.
- **Use it when:** international social networks and messengers need one
  switchable policy.
- **Overlap:** Signal is also in Privacy and Crypto so either module works alone.
- **Caution:** voice and video traffic depends on proxy UDP support and latency.

## `40-ai-developer.conf` — AI and Developer Proxy

- **Policy:** `PROXY`
- **Profiles:** advanced, full
- **Purpose:** OpenAI, Claude, Gemini, Perplexity, Copilot, Grok, GitHub, GitLab,
  Docker, npm, PyPI, Stack Overflow, Notion, and Medium.
- **Use it when:** AI and development tools should share the same proxy location.
- **Caution:** Google rules are intentionally narrow and do not proxy all Google
  traffic.

## `50-streaming.conf` — Streaming Proxy

- **Policy:** `PROXY`
- **Profiles:** minimal, advanced, full
- **Purpose:** YouTube, Netflix, Spotify, Twitch, Disney+, Max, SoundCloud, and
  their media/CDN domains.
- **Use it when:** video and music services need a foreign route.
- **Caution:** streaming consumes significant proxy bandwidth; service catalogs
  depend on proxy location.

## `60-privacy-crypto.conf` — Privacy and Crypto Proxy

- **Policy:** `PROXY`
- **Profiles:** full
- **Purpose:** secure mail, Signal/Session, Tor, privacy search, password managers,
  VPN websites, crypto exchanges and wallets, and leak-test sites.
- **Use it when:** these categories should share a stable foreign route.
- **Overlap:** Signal appears in Social and Messaging intentionally.
- **Caution:** a routing rule does not make financial or privacy activity safe or
  anonymous.

## `90-rewriters.conf` — Optional Rewriters

- **Policy:** URL Rewrite
- **Profiles:** full
- **Purpose:** redirects Google China domains to global Google.
- **Use it when:** this specific redirect is needed.
- **Caution:** URL rewrites change requests; review every expression before use.

## `95-disable-quic.conf` — Disable QUIC

- **Policy:** `REJECT` for UDP/443
- **Profiles:** none; manual opt-in only
- **Purpose:** forces applications to fall back from QUIC/HTTP3 to TCP.
- **Use it when:** diagnosing routing that is bypassed over UDP/443.
- **Caution:** may reduce performance or disrupt streaming, calls, and games.

## Intentional overlaps

The same domain with the same policy is allowed across independent modules. The
linter reports it as `INFO`. Different policies are reported as a cross-module
warning and become an error if they conflict inside a generated profile.
