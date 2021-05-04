# TradeBot

## Before Start

- Get telegram token from BotFather.
- Get token from `fixer.io`.
- Set env secrets.

Generate `SECRET` for DB.

```python
from base64 import b64encode
from os import urandom

print(b64encode(urandom(16)).decode("utf-8"))
```

```bash
export TELEGRAM_TOKEN=<secret>
export CURRENCY_TOKEN=<secret>
export SECRET=<secret>
```

## Usage

```bash
docker compose -f deployment/docker-compose.yml up -d --build
```
