"""Scatter plot — correlation between two variables.

SWD: Use scatter for showing relationships, not just dumping data. Label
notable outliers. Optional trend line. Gray most points, accent outliers.
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ── Style & colors ──────────────────────────────────────
plt.style.use(str(Path(__file__).parent.parent / 'swd.mplstyle'))

ACCENT    = '#2b5cd6'
CONTEXT   = '#a8b2c4'
TEXT_DARK  = '#1f1e1d'
TEXT_MID   = '#60739f'
TEXT_LIGHT = '#8895aa'
GRID       = '#e5e9f0'

# ── Data ────────────────────────────────────────────────
np.random.seed(42)
n = 20
provinces = [
    'Ulaanbaatar', 'Orkhon', 'Darkhan-Uul', 'Selenge', 'Tuv',
    'Bulgan', 'Arkhangai', 'Ovorkhangai', 'Dundgovi', 'Dornogovi',
    'Umnugovi', 'Bayankhongor', 'Govisumber', 'Khentii', 'Dornod',
    'Sukhbaatar', 'Zavkhan', 'Uvs', 'Khovd', 'Bayan-Olgii'
]
population = np.array([1540, 104, 87, 110, 95, 58, 86, 104, 42, 67,
                        68, 78, 17, 72, 80, 60, 65, 78, 82, 100]) * 1000
schools_per_10k = np.array([3.2, 4.1, 4.5, 5.2, 5.0, 7.1, 6.8, 6.2, 8.5, 7.0,
                            6.5, 7.3, 9.0, 6.0, 5.8, 7.5, 8.2, 7.8, 6.5, 5.5])

# Highlight outliers
highlights = {'Ulaanbaatar', 'Govisumber'}
colors = [ACCENT if p in highlights else CONTEXT for p in provinces]
sizes = [100 if p in highlights else 50 for p in provinces]

# ── Chart ───────────────────────────────────────────────
fig, ax = plt.subplots()

# Gridlines for scatter readability
ax.xaxis.grid(True, color=GRID, linewidth=0.6)
ax.yaxis.grid(True, color=GRID, linewidth=0.6)
ax.set_axisbelow(True)

# Plot points
ax.scatter(population, schools_per_10k, c=colors, s=sizes, alpha=0.85, zorder=3)

# Trend line
z = np.polyfit(population, schools_per_10k, 1)
p = np.poly1d(z)
x_line = np.linspace(min(population), max(population), 100)
ax.plot(x_line, p(x_line), color=CONTEXT, linewidth=1.2, linestyle='--', alpha=0.7)

# Label outliers
for prov, pop, spt in zip(provinces, population, schools_per_10k):
    if prov in highlights:
        offset_x = 40000 if prov == 'Ulaanbaatar' else 15000
        offset_y = 0.1
        ax.annotate(prov, xy=(pop, spt),
                    xytext=(pop + offset_x, spt + offset_y),
                    fontsize=11, fontweight='bold', color=ACCENT,
                    arrowprops=dict(arrowstyle='->', color=ACCENT, lw=1))

# Axis labels (scatter charts need them for the two dimensions)
ax.set_xlabel('Population', fontsize=13, color=TEXT_MID)
ax.set_ylabel('Schools per 10,000 residents', fontsize=13, color=TEXT_MID)

# Format x-axis with K suffix
ax.xaxis.set_major_formatter(
    plt.FuncFormatter(lambda v, _: f"{v/1000:.0f}K" if v >= 10000 else f"{v:.0f}"))

# Title & subtitle
fig.text(0.08, 0.95, "Smaller provinces have more schools per capita than Ulaanbaatar",
         fontsize=18, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
fig.text(0.08, 0.91, "Schools per 10,000 residents vs. population by province",
         fontsize=13, color=TEXT_MID, ha='left', va='top')

# Footer
fig.text(0.08, 0.02, "Source: Ministry of Education and Science of Mongolia",
         fontsize=9, color=TEXT_LIGHT, ha='left', va='bottom')

plt.savefig('scatter.png')
plt.close()
print("Saved scatter.png")
