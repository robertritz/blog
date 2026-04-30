# Secrets

The skill needs `DATAWRAPPER_API_TOKEN` in the environment. Loader is at
`scripts/_secrets.py`.

## Resolution order

1. `DATAWRAPPER_API_TOKEN` already in shell environment
2. `.env` at the blog repo root (auto-detected by walking up from the
   skill directory looking for `CLAUDE.md` + `.claude/`)
3. `.env` in the current working directory

The blog's `.gitignore` excludes `.env`, so the token never enters git
history.

## Where to put the token

`/Users/ritz/projects/blog/.env`:

```bash
DATAWRAPPER_API_TOKEN=your-token-here
```

A `.env.example` is committed to the repo so the structure is visible
without exposing the secret.

## Getting a token

Sign in at <https://app.datawrapper.de/>, then go to
<https://app.datawrapper.de/account/api-tokens>. Free plan includes API
access.

**Required scopes:**

- `chart:read`
- `chart:write`
- `folder:read`
- `folder:write`
- `theme:read`
- `user:read`

## Smoke-test

```bash
cd /Users/ritz/projects/blog
python -c "import sys; sys.path.insert(0,'.claude/skills/blog-charts/scripts'); import _secrets, _client; print(_client.me())"
```

Expected output: a JSON-ish dict with your name, email, and `chartCount`.
If you see `Missing DATAWRAPPER_API_TOKEN`, the loader didn't find the
token — check the `.env` file location and contents.

## Troubleshooting

- **"Missing DATAWRAPPER_API_TOKEN"** — `.env` not found or doesn't
  contain the key. Check the file path and re-run from the blog root.
- **HTTP 401 / 403** — token expired or lacks scopes. Generate a new
  one with the scopes above.
- **HTTP 429** — rate-limited (60 req/min). The skill auto-throttles to
  4 req/sec but bursts past that will trip it; wait a minute.
