# Raw API Reference

When the CLI scripts don't cover what you need, drop down to the API
client directly. `scripts/_client.py` exposes thin wrappers.

## Quick reference

| Function | Endpoint | Notes |
|---|---|---|
| `create_chart(title, chart_type, folder_id?, organization_id?)` | `POST /v3/charts` | Returns chart object including `id`. |
| `get_chart(chart_id)` | `GET /v3/charts/{id}` | Raises `KeyError` on 404. |
| `list_charts(limit=100, ...)` | `GET /v3/charts` | Returns `list` array. |
| `update_metadata(chart_id, patch)` | `PATCH /v3/charts/{id}` | JSON merge patch. Title and `metadata` keys. |
| `upload_data(chart_id, csv_bytes)` | `PUT /v3/charts/{id}/data` | Body is raw CSV. |
| `publish(chart_id)` | `POST /v3/charts/{id}/publish` | Returns embed codes & `publicUrl`. |
| `unpublish(chart_id)` | `POST /v3/charts/{id}/unpublish` | |
| `delete_chart(chart_id)` | `DELETE /v3/charts/{id}` | Irreversible. |
| `export_png(chart_id, zoom=2, plain=False, ...)` | `GET /v3/charts/{id}/export/png` | Returns binary PNG bytes. |
| `me()` | `GET /v3/me` | Smoke-test for auth. |

## Calling from a script

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("/Users/ritz/projects/blog/.claude/skills/blog-charts/scripts").resolve()))
import _client

# Create
chart = _client.create_chart("Title", "d3-lines")
print(chart["id"])

# Style
_client.update_metadata(chart["id"], {
    "metadata": {"describe": {"intro": "Subtitle goes here."}},
})

# Upload data
_client.upload_data(chart["id"], b"date,value\n2026-01-01,42\n")

# Publish
resp = _client.publish(chart["id"])
print(resp["data"]["publicUrl"])
```

## Rate limits

The client throttles to 0.25s between calls (4 req/sec). Datawrapper's
documented limit is 60 req/min on most routes, burstable. Bulk
operations (a 50-chart dashboard refresh) take ~13 seconds at the
throttle floor.

## Useful PATCH bodies

### Change palette to one color

```json
{
  "metadata": {
    "visualize": {
      "base-color": "#2b5cd6",
      "custom-colors": {}
    }
  }
}
```

### Per-series colors

```json
{
  "metadata": {
    "visualize": {
      "custom-colors": {
        "Gasoline": "#2b5cd6",
        "Diesel": "#d4502a"
      }
    }
  }
}
```

### Range annotation (recession bar, shortage period)

```json
{
  "metadata": {
    "visualize": {
      "range-annotations": [
        {
          "x0": "2022-02-24",
          "x1": "2022-12-31",
          "color": "#a8b2c4",
          "opacity": 0.15,
          "text": "Russia invades Ukraine"
        }
      ]
    }
  }
}
```

### Highlight one point with text annotation

```json
{
  "metadata": {
    "visualize": {
      "text-annotations": [
        {
          "x": "2024-03",
          "y": 145000,
          "text": "Peak imports",
          "size": 11,
          "color": "#60739f"
        }
      ]
    }
  }
}
```

## Datawrapper docs

- API reference: <https://developer.datawrapper.de/reference>
- Embed types & options: <https://developer.datawrapper.de/docs>
- Chart-type IDs: enumerated in `chart-types.md`
