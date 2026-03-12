"""Generate all 6 charts for the meat prices revisit post."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime

# ── Style & colors ──────────────────────────────────────
STYLE_PATH = Path.home() / 'projects/blog/.claude/skills/chart-maker/swd.mplstyle'
plt.style.use(str(STYLE_PATH))

ACCENT    = '#2b5cd6'
SECONDARY = '#d4502a'
CONTEXT   = '#a8b2c4'
TEXT_DARK  = '#1f1e1d'
TEXT_MID   = '#60739f'
TEXT_LIGHT = '#8895aa'
GRID       = '#e5e9f0'
EXTENDED   = ['#2b5cd6', '#d4502a', '#d4912a', '#2a8f5a', '#7b4ea3']

DATA_DIR = Path(__file__).parent / 'data'
OUT_DIR = Path.home() / 'projects/blog/public/images/meat-prices-2026'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_prices():
    """Load UB meat and service prices."""
    df = pd.read_csv(DATA_DIR / 'nso-0600-019v1-en.csv')
    # Only "Ulaanbaatar city" has actual values; "Ulaanbaatar" is all NaN
    ub = df[df['Region'] == 'Ulaanbaatar city'].copy()
    ub = ub.dropna(subset=['value'])
    ub['date'] = pd.to_datetime(ub['Month'], format='%Y-%m')
    return ub


def load_animal_losses():
    """Load national total animal losses by year."""
    df = pd.read_csv(DATA_DIR / 'nso-1001-029v1-en.csv')
    total = df[(df['Region'] == 'Total') & (df['Type of livestock'] == 'Total')].copy()
    total = total.dropna(subset=['value'])
    total = total.sort_values('Year')
    return total


def load_exports():
    """Load meat export data."""
    df = pd.read_csv(DATA_DIR / 'nso-1400-006v2-year-en.csv')
    # Get volume of meat exports (frozen beef, horse meat, edible offal)
    meat_items = ['Frozen beef (t)', ' Horse meat (t)', ' Edible meet offal (t)']
    volume = df[(df['Statistical indicator'] == 'Volume') &
                (df['Main commodities'].isin(meat_items))].copy()
    # Sum across meat types per year
    annual = volume.groupby('Year')['value'].sum().reset_index()
    annual.columns = ['Year', 'total_tons']
    return annual


def load_wages():
    """Load UB average wages."""
    df = pd.read_csv(DATA_DIR / 'wages-by-region-en.csv')
    ub = df[(df['Aimag'] == 'Ulaanbaatar') & (df['gender'] == 'TOTAL')].copy()
    ub = ub.drop_duplicates(subset=['TIME']).sort_values('TIME')
    # Values are in thousands of MNT
    ub['wage_mnt'] = ub['value'] * 1000
    return ub[['TIME', 'wage_mnt']].rename(columns={'TIME': 'Year'})


def load_inflation():
    """Load annual inflation rates."""
    df = pd.read_csv(DATA_DIR / 'nso-0600-013v2-en.csv')
    avg = df[df['Indicator'] == 'Inflation rate, average of the year'].copy()
    avg = avg.sort_values('Year')
    return avg[['Year', 'value']].rename(columns={'value': 'inflation_pct'})


# ═══════════════════════════════════════════════════════════
# CHART 1: The roller coaster didn't stop
# ═══════════════════════════════════════════════════════════
def chart1_price_roller_coaster():
    ub = load_prices()

    beef = ub[ub['Goods and services'].str.strip() == 'Beef, with bones, kg'].copy()
    mutton = ub[ub['Goods and services'].str.strip() == 'Mutton, with bones, kg'].copy()

    beef = beef.sort_values('date')
    mutton = mutton.sort_values('date')

    fig, ax = plt.subplots(figsize=(10, 6.5))

    ax.plot(mutton['date'], mutton['value'], color=SECONDARY, linewidth=2.5)
    ax.plot(beef['date'], beef['value'], color=ACCENT, linewidth=2.5)

    # Horizontal gridlines
    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    # Vertical dashed line at May 2019
    cutoff = datetime(2019, 5, 1)
    ax.axvline(x=cutoff, color=TEXT_MID, linestyle='--', linewidth=1, alpha=0.7)
    ax.text(cutoff, ax.get_ylim()[1] * 0.97, '  May 2019\n  (original post)',
            fontsize=9, color=TEXT_MID, va='top', ha='left')

    # Annotations for key events
    # COVID lockdown ~2020-02
    covid_date = datetime(2020, 3, 1)
    ax.annotate('COVID\nlockdown', xy=(covid_date, 11000), xytext=(datetime(2020, 10, 1), 7000),
                fontsize=9, color=TEXT_MID, ha='center',
                arrowprops=dict(arrowstyle='->', color=TEXT_MID, lw=1))

    # 2023/24 dzud - prices spike
    dzud_date = datetime(2024, 5, 1)
    ax.annotate('2023/24\ndzud', xy=(dzud_date, 22000), xytext=(datetime(2023, 1, 1), 26000),
                fontsize=9, color=TEXT_MID, ha='center',
                arrowprops=dict(arrowstyle='->', color=TEXT_MID, lw=1))

    # Direct end-labels
    last_date = beef['date'].max()
    label_x = last_date + pd.Timedelta(days=30)
    beef_last = beef.iloc[-1]['value']
    mutton_last = mutton.iloc[-1]['value']

    ax.text(label_x, beef_last, 'Beef', fontsize=10, fontweight='bold',
            color=ACCENT, va='center')
    ax.text(label_x, mutton_last, 'Mutton', fontsize=10, fontweight='bold',
            color=SECONDARY, va='center')

    # Format
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v/1000:.0f}K' if v >= 1000 else f'{v:.0f}'))
    ax.set_xlim(datetime(2010, 12, 1), last_date + pd.Timedelta(days=120))
    ax.set_ylim(0, None)

    # Title & subtitle
    fig.text(0.08, 0.95, "The roller coaster didn't stop",
             fontsize=16, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
    fig.text(0.08, 0.91, "Monthly average meat prices in Ulaanbaatar, MNT per kg | 2011\u20132026",
             fontsize=11, color=TEXT_MID, ha='left', va='top')

    fig.text(0.08, 0.02, "Source: National Statistics Office of Mongolia (1212.mn)",
             fontsize=8, color=TEXT_LIGHT, ha='left', va='bottom')

    plt.savefig(OUT_DIR / 'roller_coaster.png')
    plt.close()
    print("Saved roller_coaster.png")


# ═══════════════════════════════════════════════════════════
# CHART 2: Meat exports kept climbing
# ═══════════════════════════════════════════════════════════
def chart2_exports():
    exports = load_exports()
    exports = exports[(exports['Year'] >= 2011) & (exports['Year'] <= 2024)]
    exports = exports.dropna(subset=['total_tons'])

    fig, ax = plt.subplots(figsize=(10, 6.5))

    # Color: accent recent years (2020+), context for rest
    colors = [ACCENT if y >= 2020 else CONTEXT for y in exports['Year']]

    bars = ax.bar(exports['Year'].astype(str), exports['total_tons'], color=colors, width=0.6)

    # Label key bars
    for bar, val, year in zip(bars, exports['total_tons'], exports['Year']):
        if year in (2017, 2018, 2023, 2024):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 200,
                    f'{val:,.0f}t', ha='center', va='bottom',
                    fontsize=9, fontweight='bold',
                    color=ACCENT if year >= 2020 else TEXT_MID)

    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_ylabel('')
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=45)

    fig.text(0.08, 0.95, "Meat exports kept climbing",
             fontsize=16, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
    fig.text(0.08, 0.91, "Annual meat export volume (frozen beef, horse, offal), metric tons | 2011\u20132024",
             fontsize=11, color=TEXT_MID, ha='left', va='top')
    fig.text(0.08, 0.02, "Source: National Statistics Office of Mongolia (1212.mn)",
             fontsize=8, color=TEXT_LIGHT, ha='left', va='bottom')

    plt.savefig(OUT_DIR / 'exports.png')
    plt.close()
    print("Saved exports.png")


# ═══════════════════════════════════════════════════════════
# CHART 3: 2024 saw the worst animal losses since 2010
# ═══════════════════════════════════════════════════════════
def chart3_animal_losses():
    losses = load_animal_losses()
    losses = losses[(losses['Year'] >= 2008) & (losses['Year'] <= 2024)]
    # Values are in thousands
    losses['millions'] = losses['value'] / 1000

    fig, ax = plt.subplots(figsize=(10, 6.5))

    # Highlight 2010 and 2023/24
    colors = []
    for y in losses['Year']:
        if y == 2010:
            colors.append(SECONDARY)
        elif y in (2023, 2024):
            colors.append(ACCENT)
        else:
            colors.append(CONTEXT)

    bars = ax.bar(losses['Year'].astype(str), losses['millions'], color=colors, width=0.6)

    # Label the highlighted bars
    for bar, val, year in zip(bars, losses['millions'], losses['Year']):
        if year in (2010, 2023, 2024):
            color = SECONDARY if year == 2010 else ACCENT
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.15,
                    f'{val:.1f}M', ha='center', va='bottom',
                    fontsize=10, fontweight='bold', color=color)

    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_ylabel('')
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylim(0, None)

    fig.text(0.08, 0.95, "2024 saw the worst animal losses since 2010",
             fontsize=16, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
    fig.text(0.08, 0.91, "Adult animals lost, millions | 2008\u20132024",
             fontsize=11, color=TEXT_MID, ha='left', va='top')
    fig.text(0.08, 0.02, "Source: National Statistics Office of Mongolia (1212.mn)",
             fontsize=8, color=TEXT_LIGHT, ha='left', va='bottom')

    plt.savefig(OUT_DIR / 'animal_losses.png')
    plt.close()
    print("Saved animal_losses.png")


# ═══════════════════════════════════════════════════════════
# CHART 4: Meat is still getting cheaper relative to income
# ═══════════════════════════════════════════════════════════
def chart4_meat_income():
    """Family of 3, 250g/person/day = 750g/day. Annual cost as % of annual salary."""
    ub = load_prices()
    wages = load_wages()

    # Get annual average prices for beef and mutton in UB
    beef = ub[ub['Goods and services'].str.strip() == 'Beef, with bones, kg'].copy()
    mutton = ub[ub['Goods and services'].str.strip() == 'Mutton, with bones, kg'].copy()

    beef['year'] = beef['date'].dt.year
    mutton['year'] = mutton['date'].dt.year

    beef_annual = beef.groupby('year')['value'].mean().reset_index()
    beef_annual.columns = ['Year', 'beef_price_kg']
    mutton_annual = mutton.groupby('year')['value'].mean().reset_index()
    mutton_annual.columns = ['Year', 'mutton_price_kg']

    # Merge with wages
    merged = beef_annual.merge(mutton_annual, on='Year').merge(wages, on='Year')

    # Family of 3, 250g/person/day = 0.75 kg/day = 22.5 kg/month
    kg_per_month = 0.75 * 30  # ~22.5 kg
    merged['beef_pct'] = (merged['beef_price_kg'] * kg_per_month / merged['wage_mnt']) * 100
    merged['mutton_pct'] = (merged['mutton_price_kg'] * kg_per_month / merged['wage_mnt']) * 100

    merged = merged[(merged['Year'] >= 2011) & (merged['Year'] <= 2024)]

    fig, ax = plt.subplots(figsize=(10, 6.5))

    ax.plot(merged['Year'], merged['beef_pct'], color=ACCENT, linewidth=2.5, marker='o', markersize=4)
    ax.plot(merged['Year'], merged['mutton_pct'], color=SECONDARY, linewidth=2.5, marker='o', markersize=4)

    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    # Direct end-labels
    label_x = merged['Year'].max() + 0.3
    ax.text(label_x, merged['beef_pct'].iloc[-1], 'Beef', fontsize=10,
            fontweight='bold', color=ACCENT, va='center')
    ax.text(label_x, merged['mutton_pct'].iloc[-1], 'Mutton', fontsize=10,
            fontweight='bold', color=SECONDARY, va='center')

    ax.set_xlim(2010.5, merged['Year'].max() + 2)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}%'))
    ax.set_ylim(0, None)

    fig.text(0.08, 0.95, "Meat is still getting cheaper relative to income",
             fontsize=16, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
    fig.text(0.08, 0.91, "Monthly meat cost as % of avg UB salary (family of 3, 250g/person/day) | 2011\u20132024",
             fontsize=11, color=TEXT_MID, ha='left', va='top')
    fig.text(0.08, 0.02, "Source: National Statistics Office of Mongolia (1212.mn)",
             fontsize=8, color=TEXT_LIGHT, ha='left', va='bottom')

    plt.savefig(OUT_DIR / 'meat_income.png')
    plt.close()
    print("Saved meat_income.png")


# ═══════════════════════════════════════════════════════════
# CHART 5: The Tsuivan Index, revisited
# ═══════════════════════════════════════════════════════════
def chart5_tsuivan_index():
    """Price index with Dec 2010 = 100 for beef, mutton, canteen food, haircuts."""
    ub = load_prices()

    items = {
        'Beef': 'Beef, with bones, kg',
        'Mutton': 'Mutton, with bones, kg',
        'Canteen food': 'Canteen food',
        "Men's haircut": 'Mens haircuts',
        "Women's haircut": 'Womens haircuts, simple cuts',
    }

    fig, ax = plt.subplots(figsize=(10, 6.5))

    colors_map = {
        'Beef': ACCENT,
        'Mutton': SECONDARY,
        'Canteen food': '#d4912a',
        "Men's haircut": '#2a8f5a',
        "Women's haircut": '#7b4ea3',
    }

    # Manual label offsets to avoid overlap (adjusted after visual check)
    label_offsets = {
        'Beef': 30,
        'Mutton': -50,
        'Canteen food': 15,
        "Men's haircut": 0,
        "Women's haircut": 0,
    }

    for label, item_name in items.items():
        series = ub[ub['Goods and services'].str.strip() == item_name].copy()
        series = series.sort_values('date')
        series = series.dropna(subset=['value'])

        if len(series) == 0:
            print(f"  Warning: no data for {item_name}")
            continue

        # Get Dec 2010 base value
        base = series[series['date'] == '2010-12-01']
        if len(base) == 0:
            base_val = series.iloc[0]['value']
        else:
            base_val = base.iloc[0]['value']

        series['index'] = (series['value'] / base_val) * 100

        color = colors_map[label]
        linewidth = 2.5 if label in ('Beef', 'Mutton') else 2
        ax.plot(series['date'], series['index'], color=color, linewidth=linewidth)

        # End label with offset
        last = series.iloc[-1]
        offset = label_offsets.get(label, 0)
        ax.text(last['date'] + pd.Timedelta(days=30), last['index'] + offset,
                f'{label}\n{last["index"]:.0f}', fontsize=8.5, fontweight='bold',
                color=color, va='center')

    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    # Reference line at 100
    ax.axhline(y=100, color=TEXT_LIGHT, linewidth=0.8, linestyle='-', alpha=0.5)

    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(datetime(2010, 12, 1), datetime(2026, 10, 1))
    ax.set_ylim(50, None)

    fig.text(0.08, 0.95, "The Tsuivan Index, revisited",
             fontsize=16, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
    fig.text(0.08, 0.91, "Price index (Dec 2010 = 100) for selected goods and services in Ulaanbaatar",
             fontsize=11, color=TEXT_MID, ha='left', va='top')
    fig.text(0.08, 0.02, "Source: National Statistics Office of Mongolia (1212.mn)",
             fontsize=8, color=TEXT_LIGHT, ha='left', va='bottom')

    plt.savefig(OUT_DIR / 'tsuivan_index.png')
    plt.close()
    print("Saved tsuivan_index.png")


# ═══════════════════════════════════════════════════════════
# CHART 6: Meat prices finally outpaced inflation
# ═══════════════════════════════════════════════════════════
def chart6_inflation_comparison():
    """Actual meat prices vs what they would be if they tracked CPI."""
    ub = load_prices()
    inflation = load_inflation()

    beef = ub[ub['Goods and services'].str.strip() == 'Beef, with bones, kg'].copy()
    beef = beef.sort_values('date')
    beef = beef.dropna(subset=['value'])

    mutton = ub[ub['Goods and services'].str.strip() == 'Mutton, with bones, kg'].copy()
    mutton = mutton.sort_values('date')
    mutton = mutton.dropna(subset=['value'])

    # Build monthly CPI index from Jan 2011
    # Use annual avg inflation rate, spread monthly
    inflation = inflation.sort_values('Year')
    inflation = inflation.dropna(subset=['inflation_pct'])

    # Get Jan 2011 base prices
    beef_base = beef[beef['date'] == '2011-01-01']
    if len(beef_base) == 0:
        beef_base = beef[beef['date'].dt.year == 2011].iloc[0:1]
    beef_base_val = beef_base.iloc[0]['value']

    mutton_base = mutton[mutton['date'] == '2011-01-01']
    if len(mutton_base) == 0:
        mutton_base = mutton[mutton['date'].dt.year == 2011].iloc[0:1]
    mutton_base_val = mutton_base.iloc[0]['value']

    # Build CPI-adjusted price series
    # Start from base price, compound by annual inflation
    years = sorted(inflation['Year'].unique())
    cpi_multiplier = {2011: 1.0}
    cumulative = 1.0
    for i, yr in enumerate(years):
        if yr < 2011:
            continue
        rate = inflation[inflation['Year'] == yr]['inflation_pct'].values
        if len(rate) > 0 and yr > 2011:
            cumulative *= (1 + rate[0] / 100)
        cpi_multiplier[yr] = cumulative
    # For year 2011, we already applied the first year's inflation
    # Recalculate properly: start at 2011 base, then compound from 2012
    cpi_multiplier = {}
    cumulative = 1.0
    for yr in range(2011, 2027):
        cpi_multiplier[yr] = cumulative
        rate = inflation[inflation['Year'] == yr]['inflation_pct'].values
        if len(rate) > 0:
            cumulative *= (1 + rate[0] / 100)

    # Create CPI price for each month
    beef_cpi = []
    mutton_cpi = []
    for _, row in beef.iterrows():
        yr = row['date'].year
        if yr in cpi_multiplier:
            beef_cpi.append({'date': row['date'], 'cpi_price': beef_base_val * cpi_multiplier[yr]})
    for _, row in mutton.iterrows():
        yr = row['date'].year
        if yr in cpi_multiplier:
            mutton_cpi.append({'date': row['date'], 'cpi_price': mutton_base_val * cpi_multiplier[yr]})

    beef_cpi_df = pd.DataFrame(beef_cpi)
    mutton_cpi_df = pd.DataFrame(mutton_cpi)

    # Two-panel chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6.5), sharey=False)

    # Beef panel
    beef_plot = beef[beef['date'].dt.year >= 2011]
    ax1.plot(beef_plot['date'], beef_plot['value'], color=ACCENT, linewidth=2.5)
    ax1.plot(beef_cpi_df['date'], beef_cpi_df['cpi_price'], color=CONTEXT, linewidth=2, linestyle='--')
    ax1.set_title('Beef', fontsize=13, fontweight='bold', color=TEXT_DARK, loc='left')
    ax1.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax1.set_axisbelow(True)
    ax1.xaxis.set_major_locator(mdates.YearLocator(3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v/1000:.0f}K'))

    # Labels
    last_beef = beef_plot.iloc[-1]
    last_beef_cpi = beef_cpi_df.iloc[-1]
    ax1.text(last_beef['date'] + pd.Timedelta(days=15), last_beef['value'],
             'Actual', fontsize=9, color=ACCENT, va='center', fontweight='bold')
    ax1.text(last_beef_cpi['date'] + pd.Timedelta(days=15), last_beef_cpi['cpi_price'],
             'If tracking\nCPI', fontsize=9, color=CONTEXT, va='center')

    # Mutton panel
    mutton_plot = mutton[mutton['date'].dt.year >= 2011]
    ax2.plot(mutton_plot['date'], mutton_plot['value'], color=SECONDARY, linewidth=2.5)
    ax2.plot(mutton_cpi_df['date'], mutton_cpi_df['cpi_price'], color=CONTEXT, linewidth=2, linestyle='--')
    ax2.set_title('Mutton', fontsize=13, fontweight='bold', color=TEXT_DARK, loc='left')
    ax2.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax2.set_axisbelow(True)
    ax2.xaxis.set_major_locator(mdates.YearLocator(3))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v/1000:.0f}K'))

    last_mutton = mutton_plot.iloc[-1]
    last_mutton_cpi = mutton_cpi_df.iloc[-1]
    ax2.text(last_mutton['date'] + pd.Timedelta(days=15), last_mutton['value'],
             'Actual', fontsize=9, color=SECONDARY, va='center', fontweight='bold')
    ax2.text(last_mutton_cpi['date'] + pd.Timedelta(days=15), last_mutton_cpi['cpi_price'],
             'If tracking\nCPI', fontsize=9, color=CONTEXT, va='center')

    fig.text(0.08, 0.95, "Meat prices finally outpaced inflation",
             fontsize=16, fontweight='bold', color=TEXT_DARK, ha='left', va='top')
    fig.text(0.08, 0.91, "Actual prices vs. estimated CPI-adjusted prices, MNT per kg | 2011\u20132026",
             fontsize=11, color=TEXT_MID, ha='left', va='top')
    fig.text(0.08, 0.02, "Source: National Statistics Office of Mongolia (1212.mn)",
             fontsize=8, color=TEXT_LIGHT, ha='left', va='bottom')

    plt.tight_layout(rect=[0.05, 0.05, 0.98, 0.88])
    plt.savefig(OUT_DIR / 'inflation_comparison.png')
    plt.close()
    print("Saved inflation_comparison.png")


if __name__ == '__main__':
    print("Generating charts for meat prices revisit post...")
    print("=" * 50)
    chart1_price_roller_coaster()
    chart2_exports()
    chart3_animal_losses()
    chart4_meat_income()
    chart5_tsuivan_index()
    chart6_inflation_comparison()
    print("=" * 50)
    print("All charts generated!")
