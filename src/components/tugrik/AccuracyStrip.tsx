import type { TugrikAccuracySummary } from "~/types/tugrik"
import { formatMnt, formatRatio } from "./formatters"

interface AccuracyStripProps {
  summary: TugrikAccuracySummary
}

export function AccuracyStrip({ summary }: AccuracyStripProps) {
  return (
    <div className="tugrik-accuracy-strip">
      <div className="tugrik-metric-card">
        <span className="tugrik-metric-label">Champion model</span>
        <strong>{summary.champion_family}</strong>
        <small>{summary.champion_panel.replaceAll("_", " ")}</small>
      </div>
      <div className="tugrik-metric-card">
        <span className="tugrik-metric-label">RMSE vs random walk</span>
        <strong>{formatRatio(summary.rmse_ratio_vs_random_walk)}</strong>
        <small>Lower than 1.00 is better</small>
      </div>
      <div className="tugrik-metric-card">
        <span className="tugrik-metric-label">Directional accuracy</span>
        <strong>{(summary.directional_accuracy * 100).toFixed(0)}%</strong>
        <small>Across seeded history</small>
      </div>
      <div className="tugrik-metric-card">
        <span className="tugrik-metric-label">Latest realized miss</span>
        <strong>{formatMnt(summary.latest_abs_error, 1)}</strong>
        <small>At {summary.latest_target_period}</small>
      </div>
      <div className="tugrik-metric-card">
        <span className="tugrik-metric-label">80% interval coverage</span>
        <strong>
          {summary.coverage80 === null
            ? "n/a"
            : `${(summary.coverage80 * 100).toFixed(0)}%`}
        </strong>
        <small>Calibration check</small>
      </div>
    </div>
  )
}
