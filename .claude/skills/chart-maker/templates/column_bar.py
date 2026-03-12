"""Column (vertical) bar chart — time periods or naturally ordered categories.

SWD: Use vertical bars when the x-axis has a natural order (time, sequence).
Gray context bars, accent the key period. Direct-label key values.
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

# ── Data ────────────────────────────────────────────────
years = ['2019', '2020', '2021', '2022', '2023', '2024']
gdp_growth = [5.2, -4.4, 1.4, 5.0, 7.0, 5.3]

# Highlight: 2020 (COVID crash) and 2023 (recovery peak)
colors = []
for year, val in zip(years, gdp_growth):
    if year == '2020':
        colors.append(SECONDARY)
    elif year == '2023':
        colors.append(ACCENT)
    else:
        colors.append(CONTEXT)

# ── Chart ───────────────────────────────────────────────
fig, ax = plt.subplots()

bars = ax.bar(years, gdp_growth, color=colors, width=0.6)

# Direct labels on highlighted bars only
# NOTE: Place value labels away from the x-axis to avoid overlap with tick
# labels. For negative bars, label above the bar (inside). For positive bars,
# label above. Never place labels at the bar's terminal end near the axis.
for bar, val, year in zip(bars, gdp_growth, years):
    if year in ('2020', '2023'):
        if val < 0:
            # Label inside the bar, near the top (away from x-axis)
            y_pos = val / 2
            va = 'center'
        else:
            y_pos = val + 0.3
            va = 'bottom'
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f"{val:.1f}%", ha='center', va=va,
                fontsize=13, fontweight='bold',
                color='white' if val < 0 else (SECONDARY if year == '2020' else ACCENT))

# Light horizontal gridlines for reference
ax.yaxis.grid(True, color='#e5e9f0', linewidth=0.6)
ax.set_axisbelow(True)

# Zero line
ax.axhline(y=0, color='#c8cdd6', linewidth=0.8)

# Clean up axes
ax.set_ylabel('')
ax.set_xlabel('')
ax.tick_params(axis='x', length=0)

# Annotations
# NOTE: When iterating, check that annotation arrows don't overlap bars or
# labels. Adjust xytext position based on the actual data range.
ax.annotate('COVID-19\nshutdown', xy=(1, -4.4), xytext=(2.5, -3.0),
            fontsize=11, color=SECONDARY, ha='center',
            arrowprops=dict(arrowstyle='->', color=SECONDARY, lw=1.2))

# Title & subtitle
fig.text(0.08, 0.95, "Mongolia bounced back strongly from COVID, peaking in 2023",
         fontsize=18, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
fig.text(0.08, 0.91, "Real GDP growth rate, percent year-over-year",
         fontsize=13, color=TEXT_MID, ha='left', va='top')

# Footer
fig.text(0.08, 0.02, "Source: World Bank",
         fontsize=9, color=TEXT_LIGHT, ha='left', va='bottom')

plt.savefig('column_bar.png')
plt.close()
print("Saved column_bar.png")
