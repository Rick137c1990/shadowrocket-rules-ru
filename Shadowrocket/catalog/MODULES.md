# Shadowrocket module catalog

Этот каталог содержит модули проекта ShadowRocket Rules RU. Каждый модуль можно
подключить отдельно в зависимости от задач пользователя.

---

## Базовая конфигурация

Общая основа для работы системы правил.

- Содержит основную логику маршрутизации
- Используется как база перед подключением дополнительных модулей

https://raw.githubusercontent.com/Rick137c1990/ShadowRocket-rules-RU/refs/heads/main/Shadowrocket/base/base.conf

---

## 🇷🇺 Geo RU (геолокация России)

Правила для определения российского трафика.

- 📌 Разделение RU / NON-RU трафика
- 📌 Оптимизация маршрутов

https://raw.githubusercontent.com/Rick137c1990/ShadowRocket-rules-RU/refs/heads/main/Shadowrocket/modules/10_geo_ru.conf

---

## 🏢 Russian Services

Правила для российских сервисов.

- 📌 VK, Yandex, Mail.ru и др.
- 📌 Оптимизация доступа

https://raw.githubusercontent.com/Rick137c1990/ShadowRocket-rules-RU/refs/heads/main/Shadowrocket/modules/20_russian_services.conf

---

## 💬 VK Group

Специальные правила для VK сервисов.

- 📌 VK API
- 📌 VK media / CDN

https://raw.githubusercontent.com/Rick137c1990/ShadowRocket-rules-RU/refs/heads/main/Shadowrocket/modules/25_vk_group.conf

---

## 🔍 Yandex Group

Оптимизация сервисов Яндекса.

- 📌 Search / Maps / Music / Disk
- 📌 Отдельная маршрутизация

https://raw.githubusercontent.com/Rick137c1990/ShadowRocket-rules-RU/refs/heads/main/Shadowrocket/modules/26_yandex_group.conf

---

## 🚫 Global Blocked

Блокировка нежелательного трафика.

- 📌 Реклама
- 📌 Трекеры
- 📌 Сомнительные домены

https://raw.githubusercontent.com/Rick137c1990/ShadowRocket-rules-RU/refs/heads/main/Shadowrocket/modules/30_global_blocked.cof

---

## 🌐 Global Services

Общие международные сервисы.

- 📌 Google / Meta / GitHub / OpenAI и др.
- 📌 Базовые правила интернета

https://raw.githubusercontent.com/Rick137c1990/ShadowRocket-rules-RU/refs/heads/main/Shadowrocket/modules/40_global_servises.conf

---

## 🎬 Streaming

Правила для стриминговых сервисов.

- 📌 YouTube / Netflix / Spotify
- 📌 Оптимизация скорости и маршрута

https://raw.githubusercontent.com/Rick137c1990/ShadowRocket-rules-RU/refs/heads/main/Shadowrocket/modules/50_streaming.conf

---

## 🪙 Crypto & OpSec

Безопасность и криптовалютные сервисы.

- 📌 Crypto exchanges
- 📌 Privacy routing
- 📌 Security endpoints

https://raw.githubusercontent.com/Rick137c1990/ShadowRocket-rules-RU/refs/heads/main/Shadowrocket/modules/60_crypto_opsec.conf

---

## 🔁 Rewriters

Модуль модификации трафика.

- 📌 Rewrite rules
- 📌 Header modifications
- 📌 Advanced routing tweaks

https://raw.githubusercontent.com/Rick137c1990/ShadowRocket-rules-RU/refs/heads/main/Shadowrocket/modules/90_rewriters.conf

---
