# hookdrop

Lightweight local webhook relay with request inspection and replay support.

---

## Installation

```bash
pip install hookdrop
```

Or install from source:

```bash
git clone https://github.com/yourname/hookdrop.git && cd hookdrop && pip install -e .
```

---

## Usage

Start the relay server and forward incoming webhooks to your local service:

```bash
hookdrop start --port 9000 --forward http://localhost:3000/webhook
```

Inspect captured requests in real time:

```bash
hookdrop inspect
```

Replay a previously captured request by ID:

```bash
hookdrop replay <request-id>
```

**Example workflow:**

```bash
# Terminal 1 — start the relay
hookdrop start --port 9000 --forward http://localhost:3000/webhook

# Terminal 2 — list and replay captured requests
hookdrop list
hookdrop replay req_4f2a1b
```

Point your webhook provider (GitHub, Stripe, etc.) to `http://your-host:9000`, and hookdrop will capture, display, and forward each request to your local application.

---

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | `9000` | Port to listen on |
| `--forward` | *(required)* | Local URL to relay requests to |
| `--log` | `stdout` | Log output destination |

---

## License

MIT © [yourname](https://github.com/yourname)