# HookEcho

Minimal webhook echo tester for solo developers and micro-SaaS builders.

Create unique endpoints, send test webhooks (from Stripe, GitHub, Slack, etc.), and inspect the full request (headers, body, query).

**Signature: Mourad.Soltani**

## Features
- Generate unique short endpoint IDs
- Capture GET/POST/PUT/PATCH/DELETE
- In-memory storage (last 50 requests)
- Simple web UI
- Health check endpoint
- Fully tested

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:8000

## API

- `GET /health` — health check
- `POST /create` — create endpoint, returns `{endpoint_id, url}`
- `ANY /hook/{endpoint_id}` — capture request
- `GET /inspect/{endpoint_id}` — view captured requests
- `GET /` — simple UI

## Tests

```bash
PYTHONPATH=. pytest tests/ -v
```

All health tests must pass.

## License

MIT — see LICENSE

Built by Mourad.Soltani
