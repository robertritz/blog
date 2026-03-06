import { AxisBottom, AxisLeft } from "@visx/axis"
import { Group } from "@visx/group"
import { GridRows } from "@visx/grid"
import { ParentSize } from "@visx/responsive"
import { scaleLinear, scaleTime } from "@visx/scale"
import { LinePath } from "@visx/shape"
import { TooltipWithBounds, defaultStyles, useTooltip } from "@visx/tooltip"
import { AnimatePresence, motion } from "motion/react"
import { useMemo, useState } from "react"
import type {
  TugrikActualPoint,
  TugrikHistoryVintage,
  TugrikHorizon,
} from "~/types/tugrik"
import { formatMnt, formatPeriod, periodToDate } from "./formatters"

type TugrikChartHeight = "compact" | "standard" | "tall"

interface ForecastHistoryChartProps {
  actualSeries: TugrikActualPoint[]
  vintages: TugrikHistoryVintage[]
  selectedHorizon: TugrikHorizon
  recentWindowMonths: number
  framed?: boolean
  height?: TugrikChartHeight
  legendPlacement?: "top" | "bottom" | "none"
  showWindowControls?: boolean
}

interface HistoryTooltipData {
  label: string
  forecastValue: number
  actualValue?: number | null
  sourceLabel: string
}

export function ForecastHistoryChart({
  actualSeries,
  vintages,
  selectedHorizon,
  recentWindowMonths,
  framed = false,
  height = "standard",
  legendPlacement = "bottom",
  showWindowControls = true,
}: ForecastHistoryChartProps) {
  const [showFullHistory, setShowFullHistory] = useState(false)
  const tooltip = useTooltip<HistoryTooltipData>()

  const filtered = useMemo(() => {
    const actual = actualSeries.map((row) => ({
      date: periodToDate(row.period),
      period: row.period,
      value: row.usd_mnt,
    }))
    const horizonVintages = vintages
      .filter((row) => row.horizon_months === selectedHorizon)
      .map((row) => ({ ...row, date: periodToDate(row.target_period) }))
      .sort((a, b) => a.target_period.localeCompare(b.target_period))

    if (showFullHistory || horizonVintages.length === 0) {
      return { actual, horizonVintages }
    }

    const cutoff = subtractMonths(
      horizonVintages[horizonVintages.length - 1].target_period,
      recentWindowMonths - 1,
    )

    return {
      actual: actual.filter((row) => row.period >= cutoff),
      horizonVintages: horizonVintages.filter(
        (row) => row.target_period >= cutoff,
      ),
    }
  }, [
    actualSeries,
    recentWindowMonths,
    selectedHorizon,
    showFullHistory,
    vintages,
  ])

  const seeded = filtered.horizonVintages.filter(
    (row) => row.source_kind === "seeded_backtest",
  )
  const published = filtered.horizonVintages.filter(
    (row) => row.source_kind === "published_live",
  )

  return (
    <div
      className={`tugrik-chart-surface ${framed ? "is-framed" : "is-plain"}`}
    >
      <div className="tugrik-history-toolbar">
        <strong className="tugrik-history-label">Forecast vs actual</strong>
        {showWindowControls ? (
          <div className="tugrik-chip-row">
            <button
              type="button"
              className={`tugrik-chip${showFullHistory ? "" : "is-selected"}`}
              onClick={() => setShowFullHistory(false)}
            >
              Recent
            </button>
            <button
              type="button"
              className={`tugrik-chip${showFullHistory ? "is-selected" : ""}`}
              onClick={() => setShowFullHistory(true)}
            >
              Full
            </button>
          </div>
        ) : null}
      </div>

      {legendPlacement === "top" ? <HistoryLegend /> : null}

      <div className={`tugrik-chart-canvas is-${height}`}>
        <ParentSize>
          {({ width, height: canvasHeight }) => {
            const safeWidth = Math.max(width, 320)
            const safeHeight = Math.max(
              canvasHeight,
              getMinimumChartHeight(height),
            )
            const margin = { top: 18, right: 18, bottom: 40, left: 52 }
            const innerWidth = safeWidth - margin.left - margin.right
            const innerHeight = safeHeight - margin.top - margin.bottom
            const values = [
              ...filtered.actual.map((row) => row.value),
              ...filtered.horizonVintages.map((row) => row.forecast_value),
              ...filtered.horizonVintages.map(
                (row) => row.actual_value ?? row.forecast_value,
              ),
            ]
            const yMin = Math.min(...values)
            const yMax = Math.max(...values)
            const pad = Math.max((yMax - yMin) * 0.14, 24)
            const lastVintageDate =
              filtered.horizonVintages.length > 0
                ? filtered.horizonVintages[filtered.horizonVintages.length - 1]
                    .date
                : filtered.actual[filtered.actual.length - 1].date
            const xScale = scaleTime({
              domain: [filtered.actual[0].date, lastVintageDate],
              range: [0, innerWidth],
            })
            const yScale = scaleLinear({
              domain: [yMin - pad, yMax + pad],
              range: [innerHeight, 0],
              nice: true,
            })

            return (
              <div className="tugrik-tooltip-frame">
                <svg
                  width={safeWidth}
                  height={safeHeight}
                  role="img"
                  aria-label="Historical forecast accuracy for the selected horizon"
                >
                  <Group left={margin.left} top={margin.top}>
                    <GridRows
                      scale={yScale}
                      width={innerWidth}
                      stroke="var(--tg-grid)"
                    />

                    <LinePath
                      data={filtered.actual}
                      x={(row) => xScale(row.date) ?? 0}
                      y={(row) => yScale(row.value) ?? 0}
                      stroke="var(--tg-series-actual)"
                      strokeWidth={2.3}
                    />

                    <AnimatePresence mode="wait">
                      <motion.g
                        key={`history-${selectedHorizon}-${showFullHistory ? "full" : "recent"}`}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.14 }}
                      >
                        {seeded.length > 1 ? (
                          <LinePath
                            data={seeded}
                            x={(row) => xScale(row.date) ?? 0}
                            y={(row) => yScale(row.forecast_value) ?? 0}
                            stroke="var(--tg-series-forecast)"
                            strokeWidth={2.1}
                            strokeDasharray="7 5"
                          />
                        ) : null}
                        {published.length > 1 ? (
                          <LinePath
                            data={published}
                            x={(row) => xScale(row.date) ?? 0}
                            y={(row) => yScale(row.forecast_value) ?? 0}
                            stroke="var(--tg-series-benchmark)"
                            strokeWidth={2.1}
                          />
                        ) : null}
                      </motion.g>
                    </AnimatePresence>

                    {seeded.map((row) => {
                      const x = xScale(row.date) ?? 0
                      const y = yScale(row.forecast_value) ?? 0
                      return (
                        <circle
                          key={`seeded-${row.target_period}-${row.forecast_origin}`}
                          cx={x}
                          cy={y}
                          r={3.4}
                          fill="var(--tg-series-forecast)"
                          onMouseEnter={() =>
                            tooltip.showTooltip({
                              tooltipLeft: x + margin.left,
                              tooltipTop: y + margin.top,
                              tooltipData: {
                                label: `${formatPeriod(row.target_period)} target`,
                                forecastValue: row.forecast_value,
                                actualValue: row.actual_value,
                                sourceLabel: row.source_label,
                              },
                            })
                          }
                          onMouseLeave={tooltip.hideTooltip}
                        />
                      )
                    })}

                    {published.map((row) => {
                      const x = xScale(row.date) ?? 0
                      const y = yScale(row.forecast_value) ?? 0
                      return (
                        <rect
                          key={`published-${row.target_period}-${row.forecast_origin}`}
                          x={x - 4}
                          y={y - 4}
                          width={8}
                          height={8}
                          rx={2}
                          fill="var(--tg-series-benchmark)"
                          onMouseEnter={() =>
                            tooltip.showTooltip({
                              tooltipLeft: x + margin.left,
                              tooltipTop: y + margin.top,
                              tooltipData: {
                                label: `${formatPeriod(row.target_period)} target`,
                                forecastValue: row.forecast_value,
                                actualValue: row.actual_value,
                                sourceLabel: row.source_label,
                              },
                            })
                          }
                          onMouseLeave={tooltip.hideTooltip}
                        />
                      )
                    })}

                    <AxisLeft
                      scale={yScale}
                      numTicks={5}
                      stroke="var(--tg-grid-strong)"
                      tickStroke="var(--tg-grid-strong)"
                      tickLabelProps={() => ({
                        fill: "var(--tg-text-muted)",
                        fontSize: 11,
                        textAnchor: "end",
                        dy: "0.32em",
                      })}
                      tickFormat={(value) => formatMnt(Number(value))}
                    />

                    <AxisBottom
                      top={innerHeight}
                      scale={xScale}
                      numTicks={6}
                      stroke="var(--tg-grid-strong)"
                      tickStroke="var(--tg-grid-strong)"
                      tickLabelProps={() => ({
                        fill: "var(--tg-text-muted)",
                        fontSize: 11,
                        textAnchor: "middle",
                      })}
                      tickFormat={(value) =>
                        new Date(value.valueOf()).toLocaleDateString("en-US", {
                          month: "short",
                          year: "2-digit",
                        })
                      }
                    />
                  </Group>
                </svg>

                {tooltip.tooltipData ? (
                  <TooltipWithBounds
                    left={tooltip.tooltipLeft}
                    top={tooltip.tooltipTop}
                    style={{
                      ...defaultStyles,
                      background: "var(--tg-tooltip-bg)",
                      color: "var(--tg-tooltip-text)",
                      border: "1px solid var(--tg-grid-strong)",
                      borderRadius: 12,
                      padding: "0.75rem 0.85rem",
                      boxShadow: "0 12px 24px rgba(0, 0, 0, 0.08)",
                    }}
                  >
                    <strong>{tooltip.tooltipData.label}</strong>
                    <div>{tooltip.tooltipData.sourceLabel}</div>
                    <div>
                      Forecast:{" "}
                      {formatMnt(tooltip.tooltipData.forecastValue, 1)}
                    </div>
                    {tooltip.tooltipData.actualValue ? (
                      <div>
                        Actual: {formatMnt(tooltip.tooltipData.actualValue, 1)}
                      </div>
                    ) : (
                      <div>Actual: pending</div>
                    )}
                  </TooltipWithBounds>
                ) : null}
              </div>
            )
          }}
        </ParentSize>
      </div>

      {legendPlacement === "bottom" ? <HistoryLegend /> : null}
    </div>
  )
}

function HistoryLegend() {
  return (
    <div className="tugrik-legend">
      <span>
        <i className="is-actual" />
        Actual
      </span>
      <span>
        <i className="is-forecast" />
        Seeded backtest
      </span>
      <span>
        <i className="is-benchmark" />
        Published live
      </span>
    </div>
  )
}

function getMinimumChartHeight(height: TugrikChartHeight) {
  if (height === "compact") {
    return 310
  }

  if (height === "tall") {
    return 430
  }

  return 390
}

function subtractMonths(period: string, months: number): string {
  const [year, month] = period.split("-").map(Number)
  const date = new Date(Date.UTC(year, month - 1 - months, 1))
  return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}`
}
