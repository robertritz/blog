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


def parse_text_annotation(raw: str) -> dict:
    """Parse ``--annotate-text "X|Y|TEXT"`` into Datawrapper's text-annotation shape.

    Format: three pipe-separated fields — x position, y position, text.
    X is a string (works for date axes too). Y is a number. Text can contain
    spaces but not pipes.

    Examples::

        "2024-03|145000|Peak imports"
        "USA|72|United States"

    Optional 4th and 5th fields override color and size:
    ``"2024-03|145000|Peak imports|#c53030|12"``.

    For richer annotations (alignment, dx/dy, italic, etc.) use the raw API —
    see references/api.md.
    """
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 3:
        raise ValueError(
            f"--annotate-text must be X|Y|TEXT (got {raw!r}). "
            f"For richer annotations, use the raw API."
        )
    x, y_raw, text, *rest = parts
    try:
        # Y is usually numeric. Keep as string if it doesn't parse — works
        # for category axes.
        y: float | str = float(y_raw)
    except ValueError:
        y = y_raw
    out: dict = {
        "x": x,
        "y": y,
        "text": text,
        "color": BLOG_COLORS["text_muted"],
        "size": 11,
        "align": "mc",
        "showMobile": True,
        "showDesktop": True,
    }
    if rest:
        out["color"] = rest[0] if rest[0] else out["color"]
    if len(rest) >= 2 and rest[1]:
        try:
            out["size"] = int(rest[1])
        except ValueError:
            pass
    return out


def parse_range_annotation(raw: str) -> dict:
    """Parse ``--annotate-range "X0|X1|TEXT"`` into a range-annotation dict.

    Format: pipe-separated x0, x1, optional text. Default fill is light gray
    at ~15% opacity — reads as context, not data.

    Examples::

        "2022-02-24|2022-12-31|Russia invades Ukraine"
        "2008-09|2009-06|"   # no text, just a shaded band

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
    color = rest[1] if len(rest) >= 2 and rest[1] else BLOG_COLORS["context"]
    out: dict = {
        "x0": x0,
        "x1": x1,
        "type": "x",
        "color": color,
        "opacity": 15,
        "display": "range",
    }
    if text:
        out["text"] = text
    return out


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
