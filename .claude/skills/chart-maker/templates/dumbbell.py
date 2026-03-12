"""Dumbbell chart — before/after or gap comparisons.

SWD: Great for showing change between two time points or two conditions.
The connecting line emphasizes the gap. Sort by gap size or end value.
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
categories = ['Flour', 'Beef', 'Mutton', 'Rice', 'Potatoes', 'Milk']
before = [1800, 14000, 13000, 2800, 1500, 2200]  # 2020 prices in MNT/kg
after  = [2900, 22000, 21000, 3800, 2100, 3200]  # 2024 prices in MNT/kg

# Sort by gap (largest at top)
gaps = [a - b for a, b in zip(after, before)]
order = np.argsort(gaps)
categories = [categories[i] for i in order]
before = [before[i] for i in order]
after = [after[i] for i in order]

y = np.arange(len(categories))

# ── Chart ───────────────────────────────────────────────
fig, ax = plt.subplots()

# Connecting lines
for i in range(len(categories)):
    ax.plot([before[i], after[i]], [y[i], y[i]],
            color=CONTEXT, linewidth=1.5, zorder=1)

# Dots (no label kwarg here — legend uses separate empty artists below)
ax.scatter(before, y, color=SECONDARY, s=80, zorder=2)
ax.scatter(after, y, color=ACCENT, s=80, zorder=2)

# Direct value labels — placed to the right of both dots so they don't
# collide with category labels on the y-axis.
# NOTE: When adapting, check that value labels don't overlap category labels.
# If the "before" value is close to the y-axis, place both labels on the
# right side (after the "after" dot), or place them above/below the dots.
val_range = max(after) - min(before)
pad = val_range * 0.02

for i in range(len(categories)):
    ax.text(before[i] - pad, y[i] + 0.25, f"₮{before[i]:,}",
            ha='center', va='bottom', fontsize=11, color=SECONDARY)
    ax.text(after[i] + pad, y[i] + 0.25, f"₮{after[i]:,}",
            ha='center', va='bottom', fontsize=11, color=ACCENT)

# Category labels
ax.set_yticks(y)
ax.set_yticklabels(categories)
ax.tick_params(axis='y', length=0)

# Remove x-axis (values are directly labeled)
ax.set_xticks([])
ax.spines['bottom'].set_visible(False)

# Legend — use dedicated empty artists to avoid duplicates
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=SECONDARY,
           markersize=8, label='2020'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=ACCENT,
           markersize=8, label='2024'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11, frameon=False)

# Expand x-limits for label room
x_min = min(before) * 0.4
x_max = max(after) * 1.2
ax.set_xlim(x_min, x_max)

# Expand y-limits so top/bottom labels aren't clipped
ax.set_ylim(-0.5, len(categories) - 0.3)

# Title & subtitle
fig.text(0.08, 0.95, "Meat prices surged the most over four years",
         fontsize=18, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
fig.text(0.08, 0.91, "Price per kilogram, MNT | 2020 vs 2024",
         fontsize=13, color=TEXT_MID, ha='left', va='top')

# Footer
fig.text(0.08, 0.02, "Source: National Statistics Office of Mongolia",
         fontsize=9, color=TEXT_LIGHT, ha='left', va='bottom')

plt.savefig('dumbbell.png')
plt.close()
print("Saved dumbbell.png")
