"""Thin HTTP client for the Datawrapper API.

One reason this exists: we want one place to handle the bearer token, the
rate-limit throttle, JSON vs. text bodies, and the "network failed but let's
at least say where" error messages. The individual CLI scripts stay short
and only speak in verbs (create, update, publish, export, delete).

Datawrapper published rate limits (docs): 60 req/min per user on most routes,
burstable. We keep a 0.25s inter-call floor — slow enough to stay under
limits when iterating, fast enough that a multi-chart refresh isn't painful.

Only the standard library is used — no ``requests`` dep so this skill drops
into a minimal Python environment.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any

import _secrets

API_BASE = "https://api.datawrapper.de/v3"
_MIN_INTERVAL = 0.25
_last_call_at = 0.0


def _throttle() -> None:
    global _last_call_at
    elapsed = time.time() - _last_call_at
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _last_call_at = time.time()


def _request(
    method: str,
    path: str,
    body: bytes | None = None,
    content_type: str | None = None,
    accept: str = "application/json",
) -> tuple[int, bytes, dict[str, str]]:
    url = f"{API_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {_secrets.token()}",
        "Accept": accept,
    }
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    _throttle()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        raw = e.read() or b""
        snippet = raw[:500].decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Datawrapper API error {e.code} on {method} {path}: {snippet}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error on {method} {path}: {e.reason}") from e


# ---------- chart-level ----------


def create_chart(
    title: str,
    chart_type: str,
    folder_id: int | None = None,
    organization_id: str | None = None,
) -> dict:
    payload: dict[str, Any] = {"title": title, "type": chart_type}
    if folder_id is not None:
        payload["folderId"] = folder_id
    if organization_id is not None:
        payload["organizationId"] = organization_id
    status, raw, _ = _request(
        "POST", "/charts", json.dumps(payload).encode(), "application/json"
    )
    if status not in (200, 201):
        raise RuntimeError(f"create_chart: unexpected status {status}: {raw[:200]}")
    return json.loads(raw)


def get_chart(chart_id: str) -> dict:
    status, raw, _ = _request("GET", f"/charts/{chart_id}")
    if status == 404:
        raise KeyError(chart_id)
    if status != 200:
        raise RuntimeError(f"get_chart: {status}: {raw[:200]}")
    return json.loads(raw)


def list_charts(limit: int = 100, order_by: str = "createdAt", order: str = "DESC") -> list[dict]:
    status, raw, _ = _request(
        "GET", f"/charts?limit={limit}&orderBy={order_by}&order={order}"
    )
    if status != 200:
        raise RuntimeError(f"list_charts: {status}: {raw[:200]}")
    return json.loads(raw).get("list", [])


def update_metadata(chart_id: str, patch: dict) -> dict:
    """PATCH /charts/{id} — JSON merge patch of the whole chart object."""
    status, raw, _ = _request(
        "PATCH",
        f"/charts/{chart_id}",
        json.dumps(patch).encode(),
        "application/json",
    )
    if status != 200:
        raise RuntimeError(f"update_metadata: {status}: {raw[:200]}")
    return json.loads(raw)


def upload_data(chart_id: str, csv_bytes: bytes) -> None:
    """PUT /charts/{id}/data — raw CSV body, no response body on success."""
    status, raw, _ = _request(
        "PUT", f"/charts/{chart_id}/data", csv_bytes, "text/csv"
    )
    if status not in (200, 201, 204):
        raise RuntimeError(f"upload_data: {status}: {raw[:200]}")


def publish(chart_id: str) -> dict:
    """POST /charts/{id}/publish — returns embed codes and publicUrl."""
    status, raw, _ = _request("POST", f"/charts/{chart_id}/publish")
    if status not in (200, 201):
        raise RuntimeError(f"publish: {status}: {raw[:200]}")
    return json.loads(raw)


def unpublish(chart_id: str) -> None:
    status, raw, _ = _request("POST", f"/charts/{chart_id}/unpublish")
    if status not in (200, 204):
        raise RuntimeError(f"unpublish: {status}: {raw[:200]}")


def delete_chart(chart_id: str) -> None:
    status, raw, _ = _request("DELETE", f"/charts/{chart_id}")
    if status not in (200, 204):
        raise RuntimeError(f"delete_chart: {status}: {raw[:200]}")


def export_png(
    chart_id: str,
    zoom: int = 2,
    plain: bool = False,
    border_width: int = 20,
    width: int | None = None,
    height: int | None = None,
    transparent: bool = False,
) -> bytes:
    """GET /charts/{id}/export/png — returns binary PNG bytes.

    Works on draft AND published charts. Free tier supports PNG; PDF/SVG
    require the Custom plan.
    """
    params = [
        "unit=px",
        "mode=rgb",
        f"zoom={int(zoom)}",
        f"borderWidth={int(border_width)}",
        f"plain={'true' if plain else 'false'}",
        f"transparent={'true' if transparent else 'false'}",
    ]
    if width:
        params.append(f"width={int(width)}")
    if height:
        params.append(f"height={int(height)}")
    qs = "&".join(params)
    status, raw, _ = _request(
        "GET", f"/charts/{chart_id}/export/png?{qs}", accept="image/png"
    )
    if status != 200:
        raise RuntimeError(f"export_png: {status}: {raw[:200]}")
    return raw


# ---------- account-level ----------


def me() -> dict:
    status, raw, _ = _request("GET", "/me")
    if status != 200:
        raise RuntimeError(f"me: {status}: {raw[:200]}")
    return json.loads(raw)
