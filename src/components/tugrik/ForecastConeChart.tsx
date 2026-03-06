import { AxisBottom, AxisLeft } from "@visx/axis"
import { Group } from "@visx/group"
import { GridRows } from "@visx/grid"
import { ParentSize } from "@visx/responsive"
import { scaleLinear, scaleTime } from "@visx/scale"
import { LinePath } from "@visx/shape"
import { TooltipWithBounds, defaultStyles, useTooltip } from "@visx/tooltip"
import { motion } from "motion/react"
import type { TugrikActualPoint, TugrikForecastCard, TugrikHorizon } from "~/types/tugrik"
import { formatMnt, formatPercent, formatPeriod, periodToDate } from "./formatters"

interface ForecastConeChartProps {
  actual: TugrikActualPoint[]
  forecastPoints: TugrikForecastCard[]
  selectedHorizon: TugrikHorizon
}

interface TooltipData {
  kind: "actual" | "forecast"
  label: string
  value: number
  interval80?: [number, number]
  interval95?: [number, number]
  pctChange?: number
}

function buildBandPath(
  points: Array<{ date: Date; low: number; high: number }>,
  xScale: (value: Date) => number,
  yScale: (value: number) => number,
): string {
  if (!points.length) {
    return ""
  }
  const upper = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${xScale(point.date)} ${yScale(point.high)}`)
    .join(" ")
  const lower = points
    .slice()
    .reverse()
    .map((point) => `L ${xScale(point.date)} ${yScale(point.low)}`)
    .join(" ")
  return `${upper} ${lower} Z`
}

export function ForecastConeChart({ actual, forecastPoints, selectedHorizon }: ForecastConeChartProps) {
  const tooltip = useTooltip<TooltipData>()
  const actualPoints = actual.map((point) => ({ date: periodToDate(point.period), value: point.usd_mnt, label: point.period }))
  const forecast = forecastPoints.map((point) => ({
    ...point,
    date: periodToDate(point.target_period),
  }))
  const origin = periodToDate(forecastPoints[0].as_of_period)
  const originValue = forecastPoints[0].current_level
  const bandPoints95 = [{ date: origin, low: originValue, high: originValue }, ...forecast.map((point) => ({ date: point.date, low: point.interval95_lo, high: point.interval95_hi }))]
  const bandPoints80 = [{ date: origin, low: originValue, high: originValue }, ...forecast.map((point) => ({ date: point.date, low: point.interval80_lo, high: point.interval80_hi }))]
  const ensembleBand = [{ date: origin, low: originValue, high: originValue }, ...forecast.map((point) => ({ date: point.date, low: point.ensemble_min, high: point.ensemble_max }))]

  return (
    <div className="tugrik-chart-surface tugrik-chart-surface--hero">
      <ParentSize>
        {({ width, height }) => {
          const safeWidth = Math.max(width, 320)
          const safeHeight = Math.max(height, 360)
          const margin = { top: 16, right: 20, bottom: 36, left: 52 }
          const innerWidth = safeWidth - margin.left - margin.right
          const innerHeight = safeHeight - margin.top - margin.bottom
          const values = [
            ...actualPoints.map((point) => point.value),
            ...forecast.map((point) => point.forecast_point),
            ...forecast.map((point) => point.interval95_lo),
            ...forecast.map((point) => point.interval95_hi),
            ...forecast.map((point) => point.ensemble_min),
            ...forecast.map((point) => point.ensemble_max),
          ]
          const yMin = Math.min(...values)
          const yMax = Math.max(...values)
          const pad = (yMax - yMin) * 0.16
          const xScale = scaleTime({
            domain: [actualPoints[0].date, forecast[forecast.length - 1].date],
            range: [0, innerWidth],
          })
          const yScale = scaleLinear({
            domain: [yMin - pad, yMax + pad],
            range: [innerHeight, 0],
            nice: true,
          })
          const band95Path = buildBandPath(bandPoints95, xScale, yScale)
          const band80Path = buildBandPath(bandPoints80, xScale, yScale)
          const ensemblePath = buildBandPath(ensembleBand, xScale, yScale)

          return (
            <div className="tugrik-tooltip-frame">
              <svg width={safeWidth} height={safeHeight} role="img" aria-label="USD/MNT live forecast with uncertainty bands">
                <Group left={margin.left} top={margin.top}>
                  <GridRows
                    scale={yScale}
                    width={innerWidth}
                    stroke="var(--tg-grid)"
                    strokeOpacity={0.9}
                    pointerEvents="none"
                  />

                  <motion.path
                    d={band95Path}
                    fill="var(--tg-band-95)"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ type: "spring", stiffness: 140, damping: 20 }}
                  />
                  <motion.path
                    d={band80Path}
                    fill="var(--tg-band-80)"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ type: "spring", stiffness: 180, damping: 24, delay: 0.08 }}
                  />
                  <path d={ensemblePath} fill="var(--tg-band-ensemble)" />

                  <LinePath
                    data={actualPoints}
                    x={(point) => xScale(point.date) ?? 0}
                    y={(point) => yScale(point.value) ?? 0}
                    stroke="var(--tg-ink-strong)"
                    strokeWidth={2.4}
                  />

                  <LinePath
                    data={[{ date: origin, forecast_point: originValue }, ...forecast]}
                    x={(point) => xScale(point.date) ?? 0}
                    y={(point) => yScale(point.forecast_point) ?? 0}
                    stroke="var(--tg-accent)"
                    strokeWidth={2.4}
                    strokeDasharray="8 6"
                  />

                  <line
                    x1={xScale(origin)}
                    x2={xScale(origin)}
                    y1={0}
                    y2={innerHeight}
                    stroke="var(--tg-ink-muted)"
                    strokeDasharray="4 4"
                  />
                  <text x={xScale(origin) + 8} y={14} className="tugrik-chart-note">
                    Forecast origin
                  </text>

                  {forecast.map((point) => {
                    const x = xScale(point.date) ?? 0
                    const y = yScale(point.forecast_point) ?? 0
                    const selected = point.horizon_months === selectedHorizon
                    return (
                      <g key={point.horizon_months}>
                        <circle
                          cx={x}
                          cy={y}
                          r={selected ? 6.5 : 4.5}
                          fill={selected ? "var(--tg-accent)" : "var(--tg-paper)"}
                          stroke="var(--tg-accent)"
                          strokeWidth={selected ? 2.5 : 1.5}
                          onMouseEnter={() =>
                            tooltip.showTooltip({
                              tooltipLeft: x + margin.left,
                              tooltipTop: y + margin.top,
                              tooltipData: {
                                kind: "forecast",
                                label: `${point.horizon_months}M · ${formatPeriod(point.target_period)}`,
                                value: point.forecast_point,
                                interval80: [point.interval80_lo, point.interval80_hi],
                                interval95: [point.interval95_lo, point.interval95_hi],
                                pctChange: point.pct_change_from_current,
                              },
                            })
                          }
                          onMouseLeave={tooltip.hideTooltip}
                        />
                        <text x={x + 8} y={y - 10} className={`tugrik-chart-note${selected ? " is-active" : ""}`}>
                          {point.horizon_months}M
                        </text>
                      </g>
                    )
                  })}

                  <AxisLeft
                    scale={yScale}
                    numTicks={5}
                    stroke="var(--tg-grid-strong)"
                    tickStroke="var(--tg-grid-strong)"
                    tickLabelProps={() => ({ fill: "var(--tg-ink-muted)", fontSize: 11, textAnchor: "end", dy: "0.32em" })}
                    tickFormat={(value) => formatMnt(Number(value))}
                  />
                  <AxisBottom
                    top={innerHeight}
                    scale={xScale}
                    numTicks={6}
                    stroke="var(--tg-grid-strong)"
                    tickStroke="var(--tg-grid-strong)"
                    tickLabelProps={() => ({ fill: "var(--tg-ink-muted)", fontSize: 11, textAnchor: "middle" })}
                    tickFormat={(value) =>
                      new Date(value.valueOf()).toLocaleDateString("en-US", { month: "short", year: "2-digit" })
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
                    boxShadow: "0 14px 30px rgba(24, 22, 18, 0.16)",
                    padding: "0.75rem 0.85rem",
                  }}
                >
                  <strong>{tooltip.tooltipData.label}</strong>
                  <div>{formatMnt(tooltip.tooltipData.value, 1)} MNT per USD</div>
                  {tooltip.tooltipData.pctChange !== undefined ? (
                    <div>{formatPercent(tooltip.tooltipData.pctChange, 2)} vs current</div>
                  ) : null}
                  {tooltip.tooltipData.interval80 ? (
                    <div>
                      80%: {formatMnt(tooltip.tooltipData.interval80[0], 1)} to {formatMnt(tooltip.tooltipData.interval80[1], 1)}
                    </div>
                  ) : null}
                  {tooltip.tooltipData.interval95 ? (
                    <div>
                      95%: {formatMnt(tooltip.tooltipData.interval95[0], 1)} to {formatMnt(tooltip.tooltipData.interval95[1], 1)}
                    </div>
                  ) : null}
                </TooltipWithBounds>
              ) : null}
            </div>
          )
        }}
      </ParentSize>
    </div>
  )
}
