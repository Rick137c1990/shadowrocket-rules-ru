# Shadowrocket Rules RU — module catalog

[English](#available-modules) | [Русский](#доступные-модули)

Repository URL prefix:

```text
https://raw.githubusercontent.com/Rick137c1990/shadowrocket-rules-ru/main/Shadowrocket/
```

## Available modules

| Module | Policy | Purpose |
|---|---|---|
| [`10_geo_ru.conf`](../modules/10_geo_ru.conf) | DIRECT | Russian domains and IP addresses |
| [`20_russian_services.conf`](../modules/20_russian_services.conf) | DIRECT | Government, banks, telecom, marketplaces, transport, and media |
| [`25_vk_group.conf`](../modules/25_vk_group.conf) | DIRECT | VK, Mail.ru, OK, and MAX |
| [`26_yandex_group.conf`](../modules/26_yandex_group.conf) | DIRECT | Yandex ecosystem and infrastructure |
| [`30_social_messaging.conf`](../modules/30_social_messaging.conf) | PROXY | Social networks and messengers |
| [`40_ai_developer.conf`](../modules/40_ai_developer.conf) | PROXY | AI and developer platforms |
| [`50_streaming.conf`](../modules/50_streaming.conf) | PROXY | International video and music services |
| [`60_privacy_crypto.conf`](../modules/60_privacy_crypto.conf) | PROXY | Privacy, security, VPN, and crypto services |
| [`90_rewriters.conf`](../modules/90_rewriters.conf) | Rewrite | Optional URL redirects |
| [`95_disable_quic.conf`](../modules/95_disable_quic.conf) | REJECT | Optional UDP/443 blocking; may reduce performance |

Modules are intentionally self-contained. A domain can appear in more than one
module when both modules must work independently. The generated profiles remove
identical duplicate rules automatically.

## Доступные модули

Модули можно подключать по отдельности в зависимости от задач пользователя.
Некоторые домены намеренно встречаются в нескольких модулях, чтобы каждый модуль
работал самостоятельно. В готовых сборках одинаковые правила удаляются
автоматически.

Модуль `95_disable_quic.conf` является экспериментальным и не входит в готовые
сборки. Он блокирует UDP/443 и может ухудшить работу видео и звонков.

See the [installation guide](../../docs/instructions.md) or
[инструкцию на русском](../../docs/instructions.ru.md).
