"""Heatmap — multi-dimensional data grid.

SWD: Use sequential single-hue colormap (not rainbow). Annotate cells with
values. Good for showing patterns across two categorical dimensions.
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap

# ── Style & colors ──────────────────────────────────────
plt.style.use(str(Path(__file__).parent.parent / 'swd.mplstyle'))

ACCENT    = '#2b5cd6'
CONTEXT   = '#a8b2c4'
TEXT_DARK  = '#1f1e1d'
TEXT_MID   = '#60739f'
TEXT_LIGHT = '#8895aa'

# Sequential blue colormap harmonized with blog palette
blog_cmap = LinearSegmentedColormap.from_list(
    'blog_blue', ['#f0f3f8', '#b8c8e8', '#6b8fd4', '#2b5cd6', '#1a3a8a'])

# ── Data ────────────────────────────────────────────────
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
categories = ['Coal', 'Wind', 'Solar', 'Hydro']

# Electricity generation share (%) — illustrative
data = np.array([
    [88, 86, 78, 60, 38, 22, 15, 18, 30, 55, 75, 90],  # Coal
    [ 5,  7,  9, 12, 16, 14, 10,  8, 12, 14, 10,  6],  # Wind
    [ 1,  2,  5, 10, 18, 28, 32, 28, 18,  8,  3,  1],  # Solar
    [ 6,  5,  8, 18, 28, 36, 43, 46, 40, 23, 12,  3],  # Hydro
])

# ── Chart ───────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))

# Extra top padding so subtitle doesn't overlap top-positioned x-axis labels
fig.subplots_adjust(top=0.75)

im = ax.imshow(data, cmap=blog_cmap, aspect='auto')

# Cell annotations
for i in range(len(categories)):
    for j in range(len(months)):
        val = data[i, j]
        # White text on dark cells, dark text on light cells
        text_color = 'white' if val > 45 else TEXT_DARK
        ax.text(j, i, f"{val}%", ha='center', va='center',
                fontsize=11, color=text_color)

# Axis labels
ax.set_xticks(np.arange(len(months)))
ax.set_xticklabels(months)
ax.set_yticks(np.arange(len(categories)))
ax.set_yticklabels(categories)

# Move x-axis labels to top
ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
ax.tick_params(axis='both', length=0)

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Title & subtitle
fig.text(0.08, 0.95, "Solar and hydro peak in summer when coal retreats",
         fontsize=18, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
fig.text(0.08, 0.91, "Share of electricity generation by source, percent | Illustrative data",
         fontsize=13, color=TEXT_MID, ha='left', va='top')

# Footer
fig.text(0.08, 0.02, "Source: Energy Regulatory Commission of Mongolia",
         fontsize=9, color=TEXT_LIGHT, ha='left', va='bottom')

plt.savefig('heatmap.png')
plt.close()
print("Saved heatmap.png")
