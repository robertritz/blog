import { motion } from "motion/react"
import { useEffect, useMemo, useState } from "react"
import type { TugrikDashboardData, TugrikHorizon } from "~/types/tugrik"
import { AccuracyStrip } from "./AccuracyStrip"
import { DisclosurePanel } from "./DisclosurePanel"
import { DriversPanel } from "./DriversPanel"
import { ForecastConeChart } from "./ForecastConeChart"
import { ForecastHistoryChart } from "./ForecastHistoryChart"
import { formatMnt, formatPercent, formatPeriod } from "./formatters"
import { HorizonToggle } from "./HorizonToggle"
import { UsdCnyComparisonChart } from "./UsdCnyComparisonChart"

interface TugrikDashboardProps {
  data: TugrikDashboardData
}

/* ─────────────────────────────────────────────────────────
 * ANIMATION STORYBOARD
 *
 * Read top-to-bottom. Each `at` value is ms after mount.
 *
 *    0ms   hero forecast appears
 *  180ms   trust section settles in
 *  360ms   drivers section appears
 *  520ms   deeper detail fades in
 * ───────────────────────────────────────────────────────── */

const TIMING = {
  hero: 0,
  trust: 180,
  drivers: 360,
  detail: 520,
}

const SECTION_SPRING = {
  type: "spring" as const,
  stiffness: 180,
  damping: 24,
}

export function TugrikDashboard({ data }: TugrikDashboardProps) {
  const [stage, setStage] = useState(0)
  const [selectedHorizon, setSelectedHorizon] = useState<TugrikHorizon>(
    data.summary.default_horizon,
  )

  useEffect(() => {
    const timers = [
      window.setTimeout(() => setStage(1), TIMING.hero),
      window.setTimeout(() => setStage(2), TIMING.trust),
      window.setTimeout(() => setStage(3), TIMING.drivers),
      window.setTimeout(() => setStage(4), TIMING.detail),
    ]
    return () => timers.forEach((timer) => window.clearTimeout(timer))
  }, [])

  const selectedCard = useMemo(() => {
    return (
      data.summary.forecast_cards.find(
        (card) => card.horizon_months === selectedHorizon,
      ) ?? data.summary.forecast_cards[0]
    )
  }, [data.summary.forecast_cards, selectedHorizon])

  const accuracy = useMemo(() => {
    return (
      data.history.accuracy_by_horizon.find(
        (row) => row.horizon_months === selectedHorizon,
      ) ?? data.history.accuracy_by_horizon[0]
    )
  }, [data.history.accuracy_by_horizon, selectedHorizon])

  const drivers = data.drivers.by_horizon[String(selectedHorizon)]
  const freshnessLabel =
    data.meta.staleness_status === "fresh"
      ? "Current"
      : data.meta.staleness_status === "watch"
        ? "Watch"
        : "Stale"

  const forecastMeaning =
    selectedCard.pct_change_from_current <= 0
      ? "This points to a stronger tugrik than the aligned current level."
      : "This points to a weaker tugrik than the aligned current level."

  return (
    <div className="tugrik-dashboard">
      <motion.section
        className="tugrik-hero tugrik-hero--focus"
        initial={{ opacity: 0, y: 18 }}
        animate={stage >= 1 ? { opacity: 1, y: 0 } : {}}
        transition={SECTION_SPRING}
      >
        <div className="tugrik-hero-copy">
          <span className="tugrik-kicker">Live tugrik forecast</span>
          <h1>
            {formatMnt(selectedCard.forecast_point, 1)} by{" "}
            {formatPeriod(selectedCard.target_period)}
          </h1>
          <p className="tugrik-hero-message">
            Our {selectedHorizon}-month base case for USD/MNT. That is{" "}
            {formatPercent(selectedCard.pct_change_from_current, 2)} versus the
            aligned current level of{" "}
            {formatMnt(data.summary.current_usd_mnt, 2)}.
          </p>
          <div className="tugrik-meta-row">
            <span
              className={`tugrik-status-pill is-${data.meta.staleness_status}`}
            >
              {freshnessLabel}
            </span>
            <span>
              Aligned as of {formatPeriod(data.meta.aligned_as_of_period)}
            </span>
            <span>
              Latest spot month {formatPeriod(data.meta.latest_spot_period)}
            </span>
          </div>
          <div className="tugrik-hero-control-block">
            <span className="tugrik-control-label">Forecast horizon</span>
            <HorizonToggle
              cards={data.summary.forecast_cards}
              selectedHorizon={selectedHorizon}
              onSelect={setSelectedHorizon}
            />
          </div>
        </div>

        <div className="tugrik-callout tugrik-callout--hero">
          <span className="tugrik-stat-label">Current read</span>
          <strong>{formatMnt(selectedCard.forecast_point, 1)}</strong>
          <span>
            Base case for {formatPeriod(selectedCard.target_period)} at the{" "}
            {selectedHorizon}-month horizon
          </span>
          <dl className="tugrik-callout-facts">
            <div>
              <dt>Aligned now</dt>
              <dd>{formatMnt(data.summary.current_usd_mnt, 2)}</dd>
            </div>
            <div>
              <dt>80% range</dt>
              <dd>
                {formatMnt(selectedCard.interval80_lo, 1)} to{" "}
                {formatMnt(selectedCard.interval80_hi, 1)}
              </dd>
            </div>
            <div>
              <dt>Read</dt>
              <dd>{forecastMeaning}</dd>
            </div>
          </dl>
          <small>{selectedCard.stability_note}</small>
        </div>

        <ForecastConeChart
          actual={data.live.trailing_actual}
          forecastPoints={data.live.forecast_points}
          selectedHorizon={selectedHorizon}
        />
      </motion.section>

      <motion.section
        className="tugrik-section"
        initial={{ opacity: 0, y: 18 }}
        animate={stage >= 2 ? { opacity: 1, y: 0 } : {}}
        transition={SECTION_SPRING}
      >
        <div className="tugrik-section-head">
          <div>
            <span className="tugrik-kicker">Can we trust it?</span>
            <h2>How the forecast has actually held up.</h2>
            <p>
              Start with the simple question: has this done better than a
              no-change baseline, and how wrong has it been when it misses?
            </p>
          </div>
        </div>
        <AccuracyStrip summary={accuracy} />
        <ForecastHistoryChart
          actualSeries={data.history.actual_series}
          vintages={data.history.vintages}
          selectedHorizon={selectedHorizon}
          recentWindowMonths={data.history.recent_window_months}
        />
      </motion.section>

      <motion.section
        className="tugrik-section"
        initial={{ opacity: 0, y: 18 }}
        animate={stage >= 3 ? { opacity: 1, y: 0 } : {}}
        transition={SECTION_SPRING}
      >
        <div className="tugrik-section-head">
          <div>
            <span className="tugrik-kicker">What is moving it?</span>
            <h2>Four economic stories behind the current forecast.</h2>
            <p>
              Higher USD/MNT means a weaker tugrik. Lower USD/MNT means a
              stronger tugrik. These are the broad stories the model is leaning
              on most at the {selectedHorizon}-month horizon.
            </p>
          </div>
        </div>
        <DriversPanel
          horizon={selectedHorizon}
          bucket={drivers}
          weakerExplainer={data.drivers.explainers.weaker_tugrik}
          strongerExplainer={data.drivers.explainers.stronger_tugrik}
        />
      </motion.section>

      <motion.section
        className="tugrik-section tugrik-section--details"
        initial={{ opacity: 0, y: 18 }}
        animate={stage >= 4 ? { opacity: 1, y: 0 } : {}}
        transition={SECTION_SPRING}
      >
        <div className="tugrik-section-head">
          <div>
            <span className="tugrik-kicker">Deeper detail</span>
            <h2>Method, freshness, and supporting comparisons.</h2>
          </div>
        </div>
        <div className="tugrik-details-grid">
          <DisclosurePanel
            title="How to read this"
            summary="The short version of the forecasting workflow"
          >
            <ul className="tugrik-bullets">
              <li>
                Monthly releases are lagged so the model only uses information
                that would have been available at forecast time.
              </li>
              <li>
                The 3-month horizon is the clearest signal in this run. Longer
                horizons are shown with wider caution.
              </li>
              <li>
                Forecast bands are uncertainty ranges, not promises. They are
                meant to show how wide outcomes can plausibly get.
              </li>
            </ul>
          </DisclosurePanel>
          <DisclosurePanel
            title="Source freshness"
            summary="Current data windows behind this run"
          >
            <div className="tugrik-source-list">
              {data.meta.source_updates.map((source) => (
                <div key={source.key} className="tugrik-source-row">
                  <span>{source.label}</span>
                  <small>
                    {source.last_period
                      ? `through ${source.last_period}`
                      : "no period"}{" "}
                    ·{" "}
                    {new Date(source.updated_at).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                    })}
                  </small>
                </div>
              ))}
            </div>
          </DisclosurePanel>
          <DisclosurePanel
            title="USD vs CNY"
            summary="A supporting benchmark, not the main story"
          >
            <p className="tugrik-disclosure-copy">{data.comparison.takeaway}</p>
            <UsdCnyComparisonChart rows={data.comparison.horizons} />
          </DisclosurePanel>
          <DisclosurePanel title="Downloads" summary="Curated public artifacts">
            <div className="tugrik-download-list">
              <a href={data.downloads.dashboard_json}>Dashboard JSON</a>
              <a href={data.downloads.current_forecast_csv}>
                Current forecast CSV
              </a>
              <a href={data.downloads.forecast_vintages_csv}>
                Forecast vintages CSV
              </a>
              <a href={data.downloads.backtest_summary_csv}>
                Backtest summary CSV
              </a>
            </div>
          </DisclosurePanel>
        </div>
      </motion.section>
    </div>
  )
}
