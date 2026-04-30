"""Blog (robertritz.com) style defaults for Datawrapper charts.

Robert is on Datawrapper's Free plan, so we can't upload a custom theme.
Everything here is applied via per-chart ``metadata.visualize`` and
``metadata.publish`` — Free-tier compatible.

The "Created with Datawrapper" attribution in the footer stays (free tier
limitation). The byline, source, and notes fields are all ours to use.

Palette
-------
Harmonized with the blog's matplotlib chart-maker skill so static and
interactive charts read as one design system. The blog's CSS uses
``--accent: #2337ff`` for links; the chart accent (``#2b5cd6``) is a
slightly muted version that reads better as a fill at chart sizes.

- Primary (accent):    ``#2b5cd6``  — the data point that matters
- Secondary:           ``#d4502a``  — comparison / before-after / counter-example
- Context (gray):      ``#a8b2c4``  — background series, "everything else"
- Supporting amber:    ``#d4912a``  — third color, sparingly
- Supporting green:    ``#2a8f5a``  — fourth color, sparingly
- Supporting purple:   ``#7b4ea3``  — fifth color, last resort

Hex values chosen for:
- AA contrast against white (and the off-white plot background)
- Distinguishable for the most common form of color blindness (red-green)
- Subdued enough to read as data, not decoration

Off-white plot background (``#fafaf7``) softens the contrast vs. pure
white — an Economist convention. Gridlines: ``#e5e9f0``.
"""

from __future__ import annotations

# Ordered list — accent first, comparisons next.
BLOG_PALETTE = [
    "#2b5cd6",  # accent — primary blue, the data point that matters
    "#d4502a",  # secondary — warm orange, comparison or counterfactual
    "#d4912a",  # supporting amber, sparingly
    "#2a8f5a",  # supporting green, sparingly
    "#7b4ea3",  # supporting purple, sparingly
]

# Named colors for specific contexts.
BLOG_COLORS = {
    "accent": "#2b5cd6",
    "secondary": "#d4502a",
    "context": "#a8b2c4",   # blue-tinted gray for background series
    "positive": "#2a8f5a",
    "negative": "#c53030",
    "neutral": "#718096",
    "grid": "#e5e9f0",
    "text": "#1f1e1d",      # matches blog --gray-dark text
    "text_muted": "#60739f", # matches blog --gray
    "text_light": "#8895aa",
    "background": "#fafaf7", # off-white plot background
}

BLOG_BYLINE = "Robert Ritz"

# Chart proportions — fits the blog's 720px content column at full width.
EMBED_WIDTH = 680
EMBED_HEIGHT = 440


def base_metadata() -> dict:
    """Return the blog default metadata block.

    Callers layer describe/visualize/annotate overrides on top of this.
    Structured so a JSON merge patch against ``PATCH /charts/{id}`` produces
    a blog-styled chart in one round trip.
    """
    return {
        "describe": {
            "byline": BLOG_BYLINE,
            # source-name and source-url filled by the caller.
            "number-format": "-",
        },
        "visualize": {
            "base-color": BLOG_PALETTE[0],
            "custom-colors": {},
            "y-grid": "on",
            "x-grid": "off",
            "y-grid-format": "auto",
            "y-grid-subdivide": True,
            "show-tooltips": True,
            "interpolation": "linear",
            "value-label-colors": False,
            "thick": False,
            "label-colors": True,
        },
        "annotate": {
            "notes": "",
        },
        "publish": {
            "embed-width": EMBED_WIDTH,
            "embed-height": EMBED_HEIGHT,
            "blocks": {
                # Free tier renders the Datawrapper attribution in the footer;
                # byline & source sit next to it.
                "logo": {"enabled": False},
                "embed": True,
                "download-pdf": False,
                "download-svg": False,
                "get-the-data": True,
                "download-image": True,
            },
        },
    }


def line_defaults() -> dict:
    """Overlay for line charts (``d3-lines``)."""
    return {
        "visualize": {
            "scale-y": "linear",
            "connector-lines": True,
            "custom-range-y": ["", ""],
            "plotHeightMode": "fixed",
            "plotHeightFixed": 320,
            "label-colors": True,
            "y-grid-label-align": "left",
        },
    }


def column_defaults() -> dict:
    """Overlay for column charts (``column-chart`` and stacked/grouped variants)."""
    return {
        "visualize": {
            # Column charts must start at zero. Datawrapper already does this,
            # but be explicit so a later update doesn't accidentally clear it.
            "y-grid": "on",
            "value-labels": "hover",
            "sort-values": False,
            "reverse-order": False,
        },
    }


def bar_defaults() -> dict:
    """Overlay for horizontal bar charts (``d3-bars`` and friends)."""
    return {
        "visualize": {
            "value-label-visibility": "always",
            "value-label-alignment": "right",
            "sort-bars": False,
        },
    }


def scatter_defaults() -> dict:
    """Overlay for scatter charts (``d3-scatter-plot``)."""
    return {
        "visualize": {
            "regression": False,
            "color-by-column": False,
            "outlines": True,
        },
    }


def area_defaults() -> dict:
    """Overlay for area charts (``d3-area``)."""
    return {
        "visualize": {
            "interpolation": "linear",
            "stack-to-100": False,
        },
    }


# Map chart type → overlay function.
TYPE_OVERLAYS = {
    "d3-lines": line_defaults,
    "multiple-lines": line_defaults,
    "d3-area": area_defaults,
    "column-chart": column_defaults,
    "stacked-column-chart": column_defaults,
    "grouped-column-chart": column_defaults,
    "d3-bars": bar_defaults,
    "d3-bars-stacked": bar_defaults,
    "d3-bars-split": bar_defaults,
    "d3-scatter-plot": scatter_defaults,
}


def style_for(
    chart_type: str,
    title: str | None = None,
    intro: str | None = None,
    source_name: str | None = None,
    source_url: str | None = None,
    notes: str | None = None,
    byline: str | None = None,
    series_labels: dict | None = None,
    series_colors: dict | None = None,
    text_annotations: list | None = None,
    range_annotations: list | None = None,
    labeling: str | None = None,
    label_margin: int | None = None,
    number_format: str | None = None,
    number_append: str | None = None,
    number_prepend: str | None = None,
    extra_visualize: dict | None = None,
) -> dict:
    """Build a PATCH body that applies blog styling + caller overrides.

    ``series_labels`` maps CSV column name → display label. Used for line /
    area charts where the raw column name ("value") would otherwise show up
    in the legend.

    Returns a dict shaped like::

        {"title": ..., "metadata": {"describe": {...}, "visualize": {...},
                                    "annotate": {...}, "publish": {...}}}

    Pass it straight to ``_client.update_metadata(chart_id, patch)``.
    """
    meta = base_metadata()
    overlay = TYPE_OVERLAYS.get(chart_type)
    if overlay is not None:
        extra = overlay()
        for section, vals in extra.items():
            meta.setdefault(section, {}).update(vals)

    if source_name is not None:
        meta["describe"]["source-name"] = source_name
    if source_url is not None:
        meta["describe"]["source-url"] = source_url
    if intro is not None:
        meta["describe"]["intro"] = intro
    if byline is not None:
        meta["describe"]["byline"] = byline
    if number_format is not None:
        meta["describe"]["number-format"] = number_format
    if number_append is not None:
        meta["describe"]["number-append"] = number_append
    if number_prepend is not None:
        meta["describe"]["number-prepend"] = number_prepend
    if notes is not None:
        meta["annotate"]["notes"] = notes
    if series_labels:
        # ``visualize.lines`` takes a dict of col_name → {"title": label, ...}.
        # Merge so existing per-line settings survive.
        lines = meta["visualize"].setdefault("lines", {})
        for col, label in series_labels.items():
            lines.setdefault(col, {})["title"] = label
    if series_colors:
        # ``visualize.custom-colors`` takes a dict of series_name → "#hex".
        meta["visualize"].setdefault("custom-colors", {}).update(series_colors)
    if text_annotations:
        meta["visualize"]["text-annotations"] = list(text_annotations)
    if range_annotations:
        meta["visualize"]["range-annotations"] = list(range_annotations)
    if labeling is not None:
        meta["visualize"]["labeling"] = labeling
    if label_margin is not None:
        meta["visualize"]["label-margin"] = label_margin
    if extra_visualize:
        meta["visualize"].update(extra_visualize)

    patch: dict = {"metadata": meta}
    if title is not None:
        patch["title"] = title
    return patch


def parse_series_labels(pairs: list[str] | None) -> dict:
    """Parse ``--series-label col=label col2=label2`` CLI flags into a dict."""
    if not pairs:
        return {}
    out: dict = {}
    for raw in pairs:
        if "=" not in raw:
            raise ValueError(f"--series-label must be COL=LABEL (got {raw!r})")
        col, label = raw.split("=", 1)
        col = col.strip()
        label = label.strip()
        if not col:
            raise ValueError(f"empty column name in --series-label {raw!r}")
        out[col] = label
    return out


def parse_series_colors(pairs: list[str] | None) -> dict:
    """Parse ``--series-color SeriesName=#hex`` CLI flags into a dict.

    Hex values are passed verbatim to Datawrapper. ``#`` prefix is normalized
    in case the shell ate it.
    """
    if not pairs:
        return {}
    out: dict = {}
    for raw in pairs:
        if "=" not in raw:
            raise ValueError(f"--series-color must be SERIES=#hex (got {raw!r})")
        col, color = raw.split("=", 1)
        col = col.strip()
        color = color.strip()
        if not col:
            raise ValueError(f"empty series name in --series-color {raw!r}")
        if not color.startswith("#"):
            color = "#" + color
        out[col] = color
    return out


_DEFAULT_CONNECTOR_LINE = {
    "enabled": False,
    "type": "straight",
    "circle": False,
    "circleStyle": "solid",
    "circleRadius": 15,
    "stroke": 1,
    "arrowHead": "lines",
    "inheritColor": False,
    "targetPadding": 4,
}


def _ann_id(prefix: str) -> str:
    """Generate a short unique id for an annotation."""
    import secrets
    return f"{prefix}-{secrets.token_hex(4)}"


def _text_annotation(
    x: str | float,
    y: str | float,
    text: str,
    *,
    color: str | None = None,
    size: int = 11,
    align: str = "mc",
    dx: int = 0,
    dy: int = 0,
    italic: bool = False,
    bold: bool = False,
) -> dict:
    """Build a Datawrapper text-annotation with all required fields populated.

    Schema source: ``chartTypes.ts`` in datawrapper/datawrapper. All listed
    fields are required for the annotation to render correctly.
    """
    return {
        "id": _ann_id("txt"),
        "text": text,
        "position": {"x": x, "y": y},
        "align": align,
        "dx": dx,
        "dy": dy,
        "size": size,
        "bold": bold,
        "italic": italic,
        "underline": False,
        "color": color if color is not None else BLOG_COLORS["text_muted"],
        "bg": False,
        "width": 20,
        "showMobile": True,
        "showDesktop": True,
        "mobileFallback": True,
        "connectorLine": dict(_DEFAULT_CONNECTOR_LINE),
    }


def _range_annotation(
    x0: str | float,
    x1: str | float,
    *,
    color: str | None = None,
    opacity: int = 15,
    type_: str = "x",
    display: str = "range",
) -> dict:
    """Build a Datawrapper range-annotation with all required fields populated.

    Schema notes — confirmed empirically against Datawrapper's render service:

    - ``opacity`` is treated as a percentage 0-100 by the renderer, even though
      the TypeScript types declare it as 0-1. ``opacity: 15`` renders a faint
      band; ``opacity: 0.15`` renders nothing. Stick with 15.
    - ``position.y0`` / ``position.y1`` accept the strings ``"-Infinity"`` /
      ``"Infinity"`` to extend the band to the plot edges.
    - Range annotations have NO ``text`` field. To label a range, pair with a
      separate text-annotation — see ``label_for_range``.
    """
    return {
        "id": _ann_id("rng"),
        "position": {
            "x0": x0,
            "x1": x1,
            "y0": "-Infinity",
            "y1": "Infinity",
        },
        "display": display,
        "type": type_,
        "color": color if color is not None else BLOG_COLORS["context"],
        "opacity": opacity,
        "strokeWidth": 1,
        "strokeType": "solid",
    }


def label_for_range(
    x0: str | float,
    x1: str | float,
    text: str,
    *,
    y: float | int,
    color: str | None = None,
) -> dict:
    """Return a text-annotation positioned to label a range band.

    Datawrapper range annotations carry no text. The convention (per the
    line-chart Academy article) is to overlay a separate text annotation.
    This helper places the label inside the band, anchored at the left edge
    near the top of the data range.

    ``y`` must be a finite numeric value in **data space** — Datawrapper's
    renderer ignores text annotations whose y is non-numeric (``"95%"``,
    ``"Infinity"``, etc.). The caller computes y from the chart's data
    (typically the global max). See ``max_y_from_csv``.
    """
    return _text_annotation(
        x=x0,
        y=y,
        text=text,
        color=color if color is not None else BLOG_COLORS["text_muted"],
        size=11,
        align="tl",
        dx=4,
        dy=0,
        italic=True,
    )


def max_y_from_csv(csv_bytes: bytes) -> float | None:
    """Find the maximum numeric value across all columns in a CSV.

    Used to position auto-paired range labels. Returns ``None`` if no numeric
    values are found (e.g., the CSV is all strings or empty).

    Defensively skips:
    - The header row (first row)
    - Cells that don't parse as floats
    - Common formatting characters (commas, percent, dollar signs, spaces)
    """
    import csv as _csv
    import io as _io

    try:
        text = csv_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = csv_bytes.decode("latin-1", errors="replace")

    reader = _csv.reader(_io.StringIO(text))
    max_val: float | None = None
    for i, row in enumerate(reader):
        if i == 0:
            continue  # skip header
        for cell in row:
            cleaned = cell.strip().replace(",", "").replace("$", "").replace("%", "").replace("₮", "").strip()
            if not cleaned:
                continue
            try:
                v = float(cleaned)
            except ValueError:
                continue
            if max_val is None or v > max_val:
                max_val = v
    return max_val


def parse_text_annotation(raw: str) -> dict:
    """Parse ``--annotate-text "X|Y|TEXT"`` into a text-annotation dict.

    Format: pipe-separated — x position, y position, text. X is a string
    (works for date axes too). Y is parsed as a number when possible, kept
    as a string otherwise (for category axes or "95%" plot-relative values).

    Examples::

        "2024-03|145000|Peak imports"
        "USA|72|United States"

    Optional 4th and 5th fields override color and size:
    ``"2024-03|145000|Peak imports|#c53030|13"``.

    For richer annotations (italic/bold, dx/dy, connector lines), edit the
    returned dict — see references/datawrapper-fields.md for the full schema.
    """
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 3:
        raise ValueError(
            f"--annotate-text must be X|Y|TEXT (got {raw!r}). "
            f"For richer annotations, use the raw API."
        )
    x, y_raw, text, *rest = parts
    try:
        y: float | str = float(y_raw)
    except ValueError:
        y = y_raw  # accept "95%" or category strings verbatim
    color = rest[0] if rest and rest[0] else None
    size = 11
    if len(rest) >= 2 and rest[1]:
        try:
            size = int(rest[1])
        except ValueError:
            pass
    return _text_annotation(x=x, y=y, text=text, color=color, size=size)


def parse_range_annotation(raw: str, *, label_y: float | int | None = None) -> tuple[dict, dict | None]:
    """Parse ``--annotate-range "X0|X1|TEXT"`` into (range, optional label).

    Returns a 2-tuple:

    - The range-annotation dict (always returned).
    - A paired text-annotation dict with the label, OR ``None`` if TEXT was
      empty (just a plain shaded band).

    Datawrapper range annotations carry NO text field of their own — the
    canonical pattern is to overlay a separate text annotation. This parser
    automates that: when you pass TEXT, you get both objects back.

    ``label_y`` — required when TEXT is non-empty. The y position of the
    paired text label, in data space. The CLI computes this from the chart's
    CSV (typically the global max value) and passes it in.

    Examples::

        "2022-02-24|2022-12-31|Russia invades Ukraine"  → (range, label)
        "2008-09|2009-06|"                              → (range, None)

    Optional 4th field overrides the fill color.
    """
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 2:
        raise ValueError(
            f"--annotate-range must be X0|X1|TEXT (got {raw!r}). "
            f"TEXT can be empty for a plain shaded band."
        )
    x0, x1, *rest = parts
    text = rest[0] if rest else ""
    color = rest[1] if len(rest) >= 2 and rest[1] else None
    range_obj = _range_annotation(x0=x0, x1=x1, color=color)
    if text:
        if label_y is None:
            raise ValueError(
                f"--annotate-range with TEXT requires the caller to provide a "
                f"label y position. Got TEXT={text!r} but no label_y. "
                f"For dw_update, pass --csv so the parser can compute y from "
                f"the chart data."
            )
        label = label_for_range(x0=x0, x1=x1, text=text, y=label_y)
    else:
        label = None
    return range_obj, label


def palette_for_n(n: int) -> list[str]:
    """Return ``n`` blog palette colors, cycling if necessary."""
    if n <= 0:
        return []
    if n <= len(BLOG_PALETTE):
        return BLOG_PALETTE[:n]
    out = list(BLOG_PALETTE)
    while len(out) < n:
        out.extend(BLOG_PALETTE)
    return out[:n]


def custom_colors_for_series(series_names: list[str]) -> dict:
    """Map a list of series names to blog palette colors in order."""
    colors = palette_for_n(len(series_names))
    return {name: color for name, color in zip(series_names, colors)}
