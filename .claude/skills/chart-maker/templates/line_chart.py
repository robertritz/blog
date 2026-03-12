"""Line chart — time series, 1–3 series with direct labels.

SWD: Direct-label each line at the end (no legend box). Gray context lines,
accent the focal series. Use sparingly — more than 3 lines gets cluttered.
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ── Style & colors ──────────────────────────────────────
plt.style.use(str(Path(__file__).parent.parent / 'swd.mplstyle'))

ACCENT    = '#2b5cd6'
SECONDARY = '#d4502a'
CONTEXT   = '#a8b2c4'
TEXT_DARK  = '#1f1e1d'
TEXT_MID   = '#60739f'
TEXT_LIGHT = '#8895aa'
GRID       = '#e5e9f0'

# ── Data ────────────────────────────────────────────────
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
x = np.arange(len(months))

coal = [85, 82, 75, 55, 30, 15, 10, 12, 25, 50, 72, 88]
solar = [2, 3, 5, 8, 14, 20, 22, 19, 12, 6, 3, 2]
wind = [8, 10, 12, 15, 18, 16, 12, 10, 14, 16, 12, 9]

# ── Chart ───────────────────────────────────────────────
fig, ax = plt.subplots()

# Context lines first (behind)
ax.plot(x, wind, color=CONTEXT, linewidth=2, label='Wind')
ax.plot(x, solar, color=SECONDARY, linewidth=2.5, label='Solar')

# Focal line last (on top)
ax.plot(x, coal, color=ACCENT, linewidth=2.5, label='Coal')

# Horizontal gridlines for readability
ax.yaxis.grid(True, color=GRID, linewidth=0.6)
ax.set_axisbelow(True)

# x-axis labels
ax.set_xticks(x)
ax.set_xticklabels(months)

# y-axis formatting
ax.set_ylabel('')
ax.set_ylim(0, 100)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))

# Direct end-labels (no legend)
label_x = len(months) - 1 + 0.3

ax.text(label_x, coal[-1], 'Coal', fontsize=12, fontweight='bold',
        color=ACCENT, va='center')
ax.text(label_x, solar[-1], 'Solar', fontsize=12, fontweight='bold',
        color=SECONDARY, va='center')
ax.text(label_x, wind[-1], 'Wind', fontsize=12,
        color=CONTEXT, va='center')

# Expand x-axis to make room for labels
ax.set_xlim(-0.3, len(months) + 1.5)

# Title & subtitle
fig.text(0.08, 0.95, "Coal still dominates Mongolia's energy mix year-round",
         fontsize=18, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
fig.text(0.08, 0.91, "Share of electricity generation by source, percent | Illustrative data",
         fontsize=13, color=TEXT_MID, ha='left', va='top')

# Footer
fig.text(0.08, 0.02, "Source: Energy Regulatory Commission of Mongolia",
         fontsize=9, color=TEXT_LIGHT, ha='left', va='bottom')

plt.savefig('line_chart.png')
plt.close()
print("Saved line_chart.png")
