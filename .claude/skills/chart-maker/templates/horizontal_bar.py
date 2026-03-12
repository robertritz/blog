"""Horizontal bar chart — category comparisons, sorted by value.

SWD: Sort bars by value (largest at top). Gray everything, accent the story.
Direct-label values on or near bars. No axis needed when labels are present.
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ── Style & colors ──────────────────────────────────────
plt.style.use(str(Path(__file__).parent.parent / 'swd.mplstyle'))

ACCENT   = '#2b5cd6'
CONTEXT  = '#a8b2c4'
TEXT_DARK  = '#1f1e1d'
TEXT_MID   = '#60739f'
TEXT_LIGHT = '#8895aa'

# ── Data ────────────────────────────────────────────────
categories = [
    'Ulaanbaatar', 'Darkhan', 'Erdenet', 'Choibalsan',
    'Murun', 'Olgii', 'Dalanzadgad'
]
values = [1_540_000, 87_000, 75_000, 42_000, 38_000, 32_000, 28_000]

# Sort ascending (largest at top when plotted)
order = np.argsort(values)
categories = [categories[i] for i in order]
values = [values[i] for i in order]

# Highlight: Ulaanbaatar stands out
highlight = 'Ulaanbaatar'
colors = [ACCENT if c == highlight else CONTEXT for c in categories]

# ── Chart ───────────────────────────────────────────────
fig, ax = plt.subplots()

bars = ax.barh(categories, values, color=colors, height=0.6)

# Direct value labels
for bar, val in zip(bars, values):
    label = f"{val:,.0f}" if val < 10_000 else f"{val/1_000:.0f}K"
    ax.text(bar.get_width() + max(values) * 0.015, bar.get_y() + bar.get_height() / 2,
            label, va='center', ha='left', fontsize=12, color=TEXT_MID)

# Remove x-axis (values are directly labeled)
ax.set_xticks([])
ax.spines['bottom'].set_visible(False)

# Category labels
ax.tick_params(axis='y', length=0)
for label in ax.get_yticklabels():
    if label.get_text() == highlight:
        label.set_fontweight('bold')
        label.set_color(TEXT_DARK)

# Title & subtitle
fig.text(0.08, 0.95, "Ulaanbaatar dwarfs every other Mongolian city",
         fontsize=18, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
fig.text(0.08, 0.91, "Population by city, 2024 estimate",
         fontsize=13, color=TEXT_MID, ha='left', va='top')

# Footer
fig.text(0.08, 0.02, "Source: National Statistics Office of Mongolia",
         fontsize=9, color=TEXT_LIGHT, ha='left', va='bottom')

plt.savefig('horizontal_bar.png')
plt.close()
print("Saved horizontal_bar.png")
