"""Datawrapper token loader for the blog-charts skill.

Resolution order:
  1. DATAWRAPPER_API_TOKEN already in the shell environment
  2. .env at the blog project root (walks up from this file looking for the
     blog/CLAUDE.md marker)
  3. .env in the current working directory

The blog repo's `.gitignore` excludes `.env`, so the token never enters git
history. See `references/secrets.md`.
"""

from __future__ import annotations

import os
from pathlib import Path

TOKEN_ENV = "DATAWRAPPER_API_TOKEN"
SIGNUP_URL = "https://app.datawrapper.de/account/api-tokens"


def _project_root() -> Path | None:
    """Walk up looking for the blog repo root (has CLAUDE.md and .claude/)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "CLAUDE.md").exists() and (parent / ".claude").exists():
            return parent
    return None


def _parse_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            out[key] = value
    return out


_loaded = False
_cache: dict[str, str] = {}


def _load() -> None:
    global _loaded
    if _loaded:
        return
    candidates: list[Path] = []
    root = _project_root()
    if root is not None:
        candidates.append(root / ".env")
    candidates.append(Path.cwd() / ".env")
    for path in candidates:
        for k, v in _parse_env_file(path).items():
            _cache.setdefault(k, v)
    _loaded = True


def get(name: str, default: str | None = None) -> str | None:
    if name in os.environ and os.environ[name]:
        return os.environ[name]
    _load()
    return _cache.get(name, default)


def token() -> str:
    """Return the Datawrapper API token or exit with a signup hint."""
    val = get(TOKEN_ENV)
    if not val:
        raise SystemExit(
            f"Missing {TOKEN_ENV}. Set it in the shell or in .env at the blog repo root.\n"
            f"Create a token (free): {SIGNUP_URL}\n"
            f"Scopes needed: chart:read, chart:write, folder:read, folder:write, "
            f"theme:read, user:read."
        )
    return val
