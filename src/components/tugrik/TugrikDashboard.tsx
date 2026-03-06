import { AnimatePresence, motion } from "motion/react"
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
 *    0ms   hero summary appears
 *  180ms   forecast chart and cards settle in
 *  360ms   accuracy section slides up
 *  520ms   drivers section appears
 *  700ms   comparison and method sections fade in
 * ───────────────────────────────────────────────────────── */

const TIMING = {
  hero: 0,
  chart: 180,
  accuracy: 360,
  drivers: 520,
  detail: 700,
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
      window.setTimeout(() => setStage(2), TIMING.chart),
      window.setTimeout(() => setStage(3), TIMING.accuracy),
      window.setTimeout(() => setStage(4), TIMING.drivers),
      window.setTimeout(() => setStage(5), TIMING.detail),
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

  return (
    <div className="tugrik-dashboard">
      <motion.section
        className="tugrik-hero"
        initial={{ opacity: 0, y: 18 }}
        animate={stage >= 1 ? { opacity: 1, y: 0 } : {}}
        transition={SECTION_SPRING}
      >
        <div className="tugrik-hero-copy">
          <span className="tugrik-kicker">Live macro briefing</span>
          <h1>Forecasting the tugrik, without pretending it is easy.</h1>
          <p className="tugrik-hero-message">{data.summary.hero_message}</p>
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
        </div>
        <div className="tugrik-stat-blocks">
          <div className="tugrik-stat-card">
            <span className="tugrik-stat-label">Aligned USD/MNT</span>
            <strong>{formatMnt(data.summary.current_usd_mnt, 2)}</strong>
          </div>
          <div className="tugrik-stat-card">
            <span className="tugrik-stat-label">Aligned CNY/MNT</span>
            <strong>
              {data.summary.current_cny_mnt
                ? formatMnt(data.summary.current_cny_mnt, 2)
                : "n/a"}
            </strong>
          </div>
          <div className="tugrik-stat-card">
            <span className="tugrik-stat-label">Selected horizon</span>
            <strong>{selectedHorizon} months</strong>
          </div>
        </div>
      </motion.section>

      <motion.section
        className="tugrik-section"
        initial={{ opacity: 0, y: 18 }}
        animate={stage >= 2 ? { opacity: 1, y: 0 } : {}}
        transition={SECTION_SPRING}
      >
        <div className="tugrik-section-head">
          <div>
            <span className="tugrik-kicker">Current forecast</span>
            <h2>Where the model thinks USD/MNT is heading next.</h2>
          </div>
          <div className="tugrik-callout">
            <strong>{formatMnt(selectedCard.forecast_point, 1)}</strong>
            <span>
              {formatPercent(selectedCard.pct_change_from_current, 2)} by{" "}
              {formatPeriod(selectedCard.target_period)}
            </span>
            <small>{selectedCard.stability_note}</small>
          </div>
        </div>
        <HorizonToggle
          cards={data.summary.forecast_cards}
          selectedHorizon={selectedHorizon}
          onSelect={setSelectedHorizon}
        />
        <ForecastConeChart
          actual={data.live.trailing_actual}
          forecastPoints={data.live.forecast_points}
          selectedHorizon={selectedHorizon}
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
            <span className="tugrik-kicker">How we're doing</span>
            <h2>Actuals versus the forecast history.</h2>
            <p>
              The seeded backtest history gives immediate context. Published
              live forecasts now append on top of that, so the public track
              record grows over time.
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
        animate={stage >= 4 ? { opacity: 1, y: 0 } : {}}
        transition={SECTION_SPRING}
      >
        <div className="tugrik-section-head">
          <div>
            <span className="tugrik-kicker">What’s moving the tugrik?</span>
            <h2>Plain-language drivers for the selected horizon.</h2>
            <p>
              Higher USD/MNT means a weaker tugrik. Lower USD/MNT means a
              stronger tugrik. The bars below show which macro features the
              interpretable models lean on most for {selectedHorizon}-month
              forecasts.
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
        className="tugrik-section tugrik-section--comparison"
        initial={{ opacity: 0, y: 18 }}
        animate={stage >= 5 ? { opacity: 1, y: 0 } : {}}
        transition={SECTION_SPRING}
      >
        <div className="tugrik-section-head">
          <div>
            <span className="tugrik-kicker">USD vs CNY</span>
            <h2>How dollar and yuan forecasting compare.</h2>
            <p>{data.comparison.takeaway}</p>
          </div>
        </div>
        <UsdCnyComparisonChart rows={data.comparison.horizons} />
      </motion.section>

      <motion.section
        className="tugrik-section tugrik-section--details"
        initial={{ opacity: 0, y: 18 }}
        animate={stage >= 5 ? { opacity: 1, y: 0 } : {}}
        transition={SECTION_SPRING}
      >
        <div className="tugrik-section-head">
          <div>
            <span className="tugrik-kicker">Method & downloads</span>
            <h2>
              Enough detail for experts, without dumping everything on everyone.
            </h2>
          </div>
        </div>
        <div className="tugrik-details-grid">
          <DisclosurePanel
            title="How this works"
            summary="Leakage-safe, validation-first workflow"
          >
            <ul className="tugrik-bullets">
              <li>
                Monthly releases are lagged to approximate what would have been
                known at forecast time.
              </li>
              <li>
                Model selection is done on validation, not the final holdout
                test window.
              </li>
              <li>
                The clearest forecasting gain in this run appears around the
                3-month horizon.
              </li>
              <li>
                The 12-month forecast is shown, but it is less stable and should
                be read cautiously.
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
          <DisclosurePanel
            title="Selected horizon"
            summary={`${selectedHorizon}-month interpretation`}
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={`selected-${selectedHorizon}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
              >
                <p>
                  The {selectedHorizon}-month forecast currently points to{" "}
                  <strong>
                    {formatPercent(selectedCard.pct_change_from_current, 2)}
                  </strong>{" "}
                  relative to the aligned current level, with the center
                  forecast at{" "}
                  <strong>{formatMnt(selectedCard.forecast_point, 1)}</strong>{" "}
                  by <strong>{formatPeriod(selectedCard.target_period)}</strong>
                  .
                </p>
                <p>
                  The champion model for this horizon is{" "}
                  <strong>{selectedCard.champion_family}</strong> on{" "}
                  <strong>
                    {selectedCard.champion_panel.replaceAll("_", " ")}
                  </strong>
                  .
                </p>
              </motion.div>
            </AnimatePresence>
          </DisclosurePanel>
        </div>
      </motion.section>
    </div>
  )
}
