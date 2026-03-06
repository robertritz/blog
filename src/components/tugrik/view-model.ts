import type {
  TugrikAccuracySummary,
  TugrikDashboardData,
  TugrikDriverBucket,
  TugrikDriverLinear,
  TugrikDriverTree,
  TugrikForecastCard,
  TugrikHorizon,
  TugrikSourceUpdate,
} from "~/types/tugrik"
import {
  formatMnt,
  formatPercent,
  formatPeriod,
  formatRatio,
} from "./formatters"

export interface TugrikFactItem {
  label: string
  value: string
}

export interface TugrikDriverStory {
  key: string
  title: string
  direction: "weaker_tugrik" | "stronger_tugrik"
  summary: string
  sourceLabel: string
}

export interface TugrikSourceUpdateItem {
  key: string
  label: string
  lastPeriod: string
  updatedAt: string
}

export interface TugrikDownloadItem {
  label: string
  href: string
}

export interface TugrikDashboardViewModel {
  selectedHorizon: TugrikHorizon
  cards: TugrikForecastCard[]
  selectedCard: TugrikForecastCard
  accuracy: TugrikAccuracySummary
  bucket: TugrikDriverBucket
  pageTitle: string
  pageDeck: string
  wireDek: string
  alignedPeriod: string
  latestSpotPeriod: string
  asOfLine: string
  freshnessLabel: "Current" | "Watch" | "Stale"
  freshnessTone: "fresh" | "watch" | "stale"
  headlineValue: string
  headlinePeriod: string
  headlineDirection: string
  currentLevel: string
  changeFromCurrent: string
  range80: string
  range95: string
  facts: TugrikFactItem[]
  trustLead: string
  trustFacts: TugrikFactItem[]
  driverStories: TugrikDriverStory[]
  driverBullets: string[]
  driverLines: string[]
  methodBullets: string[]
  sourceUpdates: TugrikSourceUpdateItem[]
  strongerSignals: TugrikDriverLinear[]
  weakerSignals: TugrikDriverLinear[]
  treeSignals: TugrikDriverTree[]
  comparisonTakeaway: string
  downloads: TugrikDownloadItem[]
  historyWindowMonths: number
  historyNote: string
  rawExplainers: {
    stronger: string
    weaker: string
  }
  charts: {
    liveActual: TugrikDashboardData["live"]["trailing_actual"]
    liveForecast: TugrikDashboardData["live"]["forecast_points"]
    historyActual: TugrikDashboardData["history"]["actual_series"]
    historyVintages: TugrikDashboardData["history"]["vintages"]
    comparisonRows: TugrikDashboardData["comparison"]["horizons"]
  }
}

interface StoryDefinition {
  key: string
  title: string
  match: RegExp[]
  weakerSummary: string
  strongerSummary: string
}

const STORY_DEFINITIONS: StoryDefinition[] = [
  {
    key: "inflation",
    title: "Inflation pressure",
    match: [/inflation/i, /cpi/i],
    weakerSummary:
      "Higher inflation pressure is usually associated with a weaker tugrik later on.",
    strongerSummary:
      "Cooling inflation pressure usually leaves more room for the tugrik to hold firm.",
  },
  {
    key: "dollar_strength",
    title: "Global dollar strength",
    match: [/broad usd/i, /\busd index\b/i, /\bdxy\b/i],
    weakerSummary:
      "A stronger global dollar backdrop often pushes USD/MNT higher as well.",
    strongerSummary:
      "A softer global dollar backdrop usually gives the tugrik some breathing room.",
  },
  {
    key: "trade_balance",
    title: "Trade balance",
    match: [/trade balance/i, /foreign trade/i],
    weakerSummary:
      "A softer trade position usually leaves the tugrik with less support.",
    strongerSummary:
      "A stronger trade position usually adds support for the tugrik.",
  },
  {
    key: "capital_flows",
    title: "Capital and external flows",
    match: [/financial account/i, /net errors/i, /reserve/i],
    weakerSummary:
      "Weaker external financing tends to leave the tugrik more exposed.",
    strongerSummary:
      "Stronger capital and external financing tends to cushion the tugrik.",
  },
  {
    key: "commodity_prices",
    title: "Commodity prices",
    match: [/coal/i, /copper/i, /gold/i, /brent/i, /oil/i],
    weakerSummary:
      "Softer export-price conditions can reduce foreign-currency inflows and weigh on the tugrik.",
    strongerSummary:
      "Better export-price conditions can support foreign-currency inflows and help the tugrik.",
  },
  {
    key: "china_link",
    title: "China-linked demand",
    match: [/cny/i, /neer/i],
    weakerSummary:
      "China-linked currency and demand signals can spill over into tugrik pressure.",
    strongerSummary:
      "Healthier China-linked conditions can give the tugrik extra support.",
  },
]

export function buildTugrikViewModel(
  data: TugrikDashboardData,
  selectedHorizon: TugrikHorizon,
): TugrikDashboardViewModel {
  const selectedCard =
    data.summary.forecast_cards.find(
      (card) => card.horizon_months === selectedHorizon,
    ) ?? data.summary.forecast_cards[0]
  const accuracy =
    data.history.accuracy_by_horizon.find(
      (row) => row.horizon_months === selectedHorizon,
    ) ?? data.history.accuracy_by_horizon[0]
  const bucket =
    data.drivers.by_horizon[String(selectedHorizon)] ??
    data.drivers.by_horizon[String(data.summary.default_horizon)]
  const stories = buildStories(bucket)
  const freshnessLabel = getFreshnessLabel(data.meta.staleness_status)
  const changeLabel = formatPercent(selectedCard.pct_change_from_current, 2)
  const trustLead = buildTrustLead(selectedHorizon, accuracy)

  return {
    selectedHorizon,
    cards: data.summary.forecast_cards,
    selectedCard,
    accuracy,
    bucket,
    pageTitle: "USD/MNT Forecast",
    pageDeck: `${selectedHorizon}-month base case: ${formatMnt(selectedCard.forecast_point, 1)} by ${formatPeriod(selectedCard.target_period)}, ${changeLabel} versus the aligned current level.`,
    wireDek: `${selectedHorizon}M base case is ${formatMnt(selectedCard.forecast_point, 1)} by ${formatPeriod(selectedCard.target_period)}.`,
    alignedPeriod: formatPeriod(data.meta.aligned_as_of_period),
    latestSpotPeriod: formatPeriod(data.meta.latest_spot_period),
    asOfLine: `As of ${formatPeriod(data.meta.aligned_as_of_period)}. Latest spot month ${formatPeriod(data.meta.latest_spot_period)}.`,
    freshnessLabel,
    freshnessTone: data.meta.staleness_status,
    headlineValue: formatMnt(selectedCard.forecast_point, 1),
    headlinePeriod: formatPeriod(selectedCard.target_period),
    headlineDirection:
      selectedCard.pct_change_from_current <= 0
        ? "Stronger tugrik than the aligned current level"
        : "Weaker tugrik than the aligned current level",
    currentLevel: formatMnt(data.summary.current_usd_mnt, 2),
    changeFromCurrent: changeLabel,
    range80: `${formatMnt(selectedCard.interval80_lo, 1)} to ${formatMnt(selectedCard.interval80_hi, 1)}`,
    range95: `${formatMnt(selectedCard.interval95_lo, 1)} to ${formatMnt(selectedCard.interval95_hi, 1)}`,
    facts: [
      {
        label: "Base case",
        value: `${formatMnt(selectedCard.forecast_point, 1)} by ${formatPeriod(selectedCard.target_period)}`,
      },
      {
        label: "Vs current",
        value: `${changeLabel} vs ${formatMnt(data.summary.current_usd_mnt, 2)}`,
      },
      {
        label: "80% range",
        value: `${formatMnt(selectedCard.interval80_lo, 1)} to ${formatMnt(selectedCard.interval80_hi, 1)}`,
      },
      {
        label: "Latest miss",
        value: `${formatMnt(accuracy.latest_abs_error, 1)} at ${formatPeriod(accuracy.latest_target_period)}`,
      },
    ],
    trustLead,
    trustFacts: [
      {
        label: "RMSE vs no-change",
        value: formatRatio(accuracy.rmse_ratio_vs_random_walk),
      },
      {
        label: "Direction right",
        value: `${Math.round(accuracy.directional_accuracy * 100)}%`,
      },
      {
        label: "Recent MAE",
        value: `${formatMnt(accuracy.recent_mae, 1)} MNT`,
      },
      {
        label: "Coverage 80 / 95",
        value: `${formatCoverage(accuracy.coverage80)} / ${formatCoverage(accuracy.coverage95)}`,
      },
      {
        label: "Champion",
        value: `${accuracy.champion_family.replaceAll("_", " ")} · ${accuracy.champion_panel.replaceAll("_", " ")}`,
      },
    ],
    driverStories: stories,
    driverBullets: stories.map(
      (story) =>
        `${story.title}: ${story.summary} Main signal now: ${story.sourceLabel}.`,
    ),
    driverLines: stories.map((story) =>
      story.direction === "weaker_tugrik"
        ? `${story.title} leans weaker tugrik. Main signal: ${story.sourceLabel}.`
        : `${story.title} supports the tugrik. Main signal: ${story.sourceLabel}.`,
    ),
    methodBullets: [
      "The model only uses information that would have been available at forecast time.",
      "Lower RMSE ratios are better. Anything below 1.00x beats a no-change baseline for this horizon.",
      "Forecast bands are uncertainty ranges, not promises.",
    ],
    sourceUpdates: data.meta.source_updates.map(formatSourceUpdate),
    strongerSignals: bucket.negative.filter((driver) => driver.strength > 0),
    weakerSignals: bucket.positive.filter((driver) => driver.strength > 0),
    treeSignals: bucket.tree.slice(0, 8),
    comparisonTakeaway: data.comparison.takeaway,
    downloads: [
      {
        label: "Dashboard JSON",
        href: data.downloads.dashboard_json,
      },
      {
        label: "Current forecast CSV",
        href: data.downloads.current_forecast_csv,
      },
      {
        label: "Forecast vintages CSV",
        href: data.downloads.forecast_vintages_csv,
      },
      {
        label: "Backtest summary CSV",
        href: data.downloads.backtest_summary_csv,
      },
    ],
    historyWindowMonths: data.history.recent_window_months,
    historyNote:
      "Seeded backtests simulate what the page would have shown in earlier periods. Published live points are the real monthly forecasts from this dashboard going forward.",
    rawExplainers: {
      stronger: data.drivers.explainers.stronger_tugrik,
      weaker: data.drivers.explainers.weaker_tugrik,
    },
    charts: {
      liveActual: data.live.trailing_actual,
      liveForecast: data.live.forecast_points,
      historyActual: data.history.actual_series,
      historyVintages: data.history.vintages,
      comparisonRows: data.comparison.horizons,
    },
  }
}

function buildTrustLead(
  horizon: TugrikHorizon,
  accuracy: TugrikAccuracySummary,
): string {
  if (accuracy.rmse_ratio_vs_random_walk < 1) {
    return `${horizon}M backtests beat no-change at ${formatRatio(accuracy.rmse_ratio_vs_random_walk)} of baseline RMSE and get direction right ${Math.round(accuracy.directional_accuracy * 100)}% of the time.`
  }

  return `${horizon}M backtests are roughly in line with a no-change baseline, with ${Math.round(accuracy.directional_accuracy * 100)}% directional accuracy so far.`
}

function buildStories(bucket: TugrikDriverBucket): TugrikDriverStory[] {
  const strongestByStory = new Map<string, TugrikDriverLinear>()

  for (const driver of [...bucket.positive, ...bucket.negative]) {
    const definition = matchStory(driver)
    const existing = strongestByStory.get(definition.key)
    if (!existing || driver.strength > existing.strength) {
      strongestByStory.set(definition.key, driver)
    }
  }

  return Array.from(strongestByStory.values())
    .sort((a, b) => b.strength - a.strength)
    .slice(0, 4)
    .map((driver) => {
      const definition = matchStory(driver)
      return {
        key: definition.key,
        title: definition.title,
        direction: driver.direction,
        summary:
          driver.direction === "weaker_tugrik"
            ? definition.weakerSummary
            : definition.strongerSummary,
        sourceLabel: driver.label,
      }
    })
}

function matchStory(driver: TugrikDriverLinear): StoryDefinition {
  const haystack = `${driver.feature} ${driver.label}`.toLowerCase()
  return (
    STORY_DEFINITIONS.find((definition) =>
      definition.match.some((pattern) => pattern.test(haystack)),
    ) ?? {
      key: driver.feature,
      title: driver.label,
      match: [],
      weakerSummary: driver.interpretation,
      strongerSummary: driver.interpretation,
    }
  )
}

function formatSourceUpdate(
  source: TugrikSourceUpdate,
): TugrikSourceUpdateItem {
  return {
    key: source.key,
    label: source.label,
    lastPeriod: source.last_period
      ? `through ${formatPeriod(source.last_period)}`
      : "period unavailable",
    updatedAt: new Date(source.updated_at).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    }),
  }
}

function formatCoverage(value: number | null): string {
  if (value === null) {
    return "n/a"
  }

  return `${Math.round(value * 100)}%`
}

function getFreshnessLabel(status: "fresh" | "watch" | "stale") {
  if (status === "fresh") {
    return "Current" as const
  }
  if (status === "watch") {
    return "Watch" as const
  }
  return "Stale" as const
}
