import { AxisBottom, AxisLeft } from "@visx/axis"
import { Group } from "@visx/group"
import { GridRows } from "@visx/grid"
import { ParentSize } from "@visx/responsive"
import { scaleLinear, scaleTime } from "@visx/scale"
import { LinePath } from "@visx/shape"
import { TooltipWithBounds, defaultStyles, useTooltip } from "@visx/tooltip"
import type {
  TugrikActualPoint,
  TugrikForecastCard,
  TugrikHorizon,
} from "~/types/tugrik"
import { formatMnt, formatPercent, periodToDate } from "./formatters"

type TugrikChartHeight = "compact" | "standard" | "tall"

interface ForecastConeChartProps {
  actual: TugrikActualPoint[]
  forecastPoints: TugrikForecastCard[]
  selectedHorizon: TugrikHorizon
  framed?: boolean
  height?: TugrikChartHeight
  annotationDensity?: "full" | "minimal"
}

interface TooltipData {
  label: string
  value: number
  interval80: [number, number]
  interval95: [number, number]
  pctChange: number
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
    .map(
      (point, index) =>
        `${index === 0 ? "M" : "L"} ${xScale(point.date)} ${yScale(point.high)}`,
    )
    .join(" ")
  const lower = points
    .slice()
    .reverse()
    .map((point) => `L ${xScale(point.date)} ${yScale(point.low)}`)
    .join(" ")

  return `${upper} ${lower} Z`
}

export function ForecastConeChart({
  actual,
  forecastPoints,
  selectedHorizon,
  framed = false,
  height = "standard",
  annotationDensity = "full",
}: ForecastConeChartProps) {
  const tooltip = useTooltip<TooltipData>()
  const actualPoints = actual.map((point) => ({
    date: periodToDate(point.period),
    value: point.usd_mnt,
  }))
  const forecast = forecastPoints.map((point) => ({
    ...point,
    date: periodToDate(point.target_period),
  }))
  const origin = periodToDate(forecastPoints[0].as_of_period)
  const originValue = forecastPoints[0].current_level
  const band95 = [
    { date: origin, low: originValue, high: originValue },
    ...forecast.map((point) => ({
      date: point.date,
      low: point.interval95_lo,
      high: point.interval95_hi,
    })),
  ]
  const band80 = [
    { date: origin, low: originValue, high: originValue },
    ...forecast.map((point) => ({
      date: point.date,
      low: point.interval80_lo,
      high: point.interval80_hi,
    })),
  ]

  return (
    <div
      className={`tugrik-chart-surface${framed ? "is-framed" : "is-plain"} is-${height}`}
    >
      <ParentSize>
        {({ width, height: surfaceHeight }) => {
          const safeWidth = Math.max(width, 320)
          const safeHeight = Math.max(
            surfaceHeight,
            height === "compact" ? 300 : 360,
          )
          const margin = { top: 16, right: 20, bottom: 36, left: 52 }
          const innerWidth = safeWidth - margin.left - margin.right
          const innerHeight = safeHeight - margin.top - margin.bottom
          const values = [
            ...actualPoints.map((point) => point.value),
            ...forecast.map((point) => point.forecast_point),
            ...forecast.map((point) => point.interval95_lo),
            ...forecast.map((point) => point.interval95_hi),
          ]
          const yMin = Math.min(...values)
          const yMax = Math.max(...values)
          const pad = Math.max((yMax - yMin) * 0.16, 24)
          const xScale = scaleTime({
            domain: [actualPoints[0].date, forecast[forecast.length - 1].date],
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
                aria-label="USD/MNT live forecast with uncertainty bands"
              >
                <Group left={margin.left} top={margin.top}>
                  <GridRows
                    scale={yScale}
                    width={innerWidth}
                    stroke="var(--tg-grid)"
                    pointerEvents="none"
                  />

                  <path
                    d={buildBandPath(band95, xScale, yScale)}
                    fill="var(--tg-band-95)"
                  />
                  <path
                    d={buildBandPath(band80, xScale, yScale)}
                    fill="var(--tg-band-80)"
                  />

                  <LinePath
                    data={actualPoints}
                    x={(point) => xScale(point.date) ?? 0}
                    y={(point) => yScale(point.value) ?? 0}
                    stroke="var(--tg-series-actual)"
                    strokeWidth={2.4}
                  />

                  <LinePath
                    data={[
                      { date: origin, forecast_point: originValue },
                      ...forecast,
                    ]}
                    x={(point) => xScale(point.date) ?? 0}
                    y={(point) => yScale(point.forecast_point) ?? 0}
                    stroke="var(--tg-series-forecast)"
                    strokeWidth={2.3}
                    strokeDasharray="8 6"
                  />

                  <path
                    d={buildBandPath(band80, xScale, yScale)}
                    fill="none"
                    stroke="var(--tg-series-forecast)"
                    strokeOpacity={0.18}
                    strokeWidth={1}
                  />

                  <line
                    x1={xScale(origin)}
                    x2={xScale(origin)}
                    y1={0}
                    y2={innerHeight}
                    stroke="var(--tg-grid-strong)"
                    strokeDasharray="4 4"
                  />

                  {annotationDensity === "full" ? (
                    <text
                      x={xScale(origin) + 8}
                      y={14}
                      className="tugrik-chart-note"
                    >
                      Forecast origin
                    </text>
                  ) : null}

                  {forecast.map((point) => {
                    const x = xScale(point.date) ?? 0
                    const y = yScale(point.forecast_point) ?? 0
                    const selected = point.horizon_months === selectedHorizon
                    const showLabel = annotationDensity === "full" || selected

                    return (
                      <g key={point.horizon_months}>
                        <circle
                          cx={x}
                          cy={y}
                          r={selected ? 5.5 : 4}
                          fill={
                            selected ? "white" : "var(--tg-series-forecast)"
                          }
                          stroke="var(--tg-series-forecast)"
                          strokeWidth={selected ? 2.5 : 1.5}
                          onMouseEnter={() =>
                            tooltip.showTooltip({
                              tooltipLeft: x + margin.left,
                              tooltipTop: y + margin.top,
                              tooltipData: {
                                label: `${point.horizon_months}M target`,
                                value: point.forecast_point,
                                interval80: [
                                  point.interval80_lo,
                                  point.interval80_hi,
                                ],
                                interval95: [
                                  point.interval95_lo,
                                  point.interval95_hi,
                                ],
                                pctChange: point.pct_change_from_current,
                              },
                            })
                          }
                          onMouseLeave={tooltip.hideTooltip}
                        />
                        {showLabel ? (
                          <text
                            x={x + 8}
                            y={y - 10}
                            className={`tugrik-chart-note${selected ? "is-active" : ""}`}
                          >
                            {point.horizon_months}M
                          </text>
                        ) : null}
                      </g>
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
                    boxShadow: "0 12px 24px rgba(0, 0, 0, 0.08)",
                    padding: "0.75rem 0.85rem",
                  }}
                >
                  <strong>{tooltip.tooltipData.label}</strong>
                  <div>
                    {formatMnt(tooltip.tooltipData.value, 1)} MNT per USD
                  </div>
                  <div>
                    {formatPercent(tooltip.tooltipData.pctChange, 2)} vs current
                  </div>
                  <div>
                    80%: {formatMnt(tooltip.tooltipData.interval80[0], 1)} to{" "}
                    {formatMnt(tooltip.tooltipData.interval80[1], 1)}
                  </div>
                  <div>
                    95%: {formatMnt(tooltip.tooltipData.interval95[0], 1)} to{" "}
                    {formatMnt(tooltip.tooltipData.interval95[1], 1)}
                  </div>
                </TooltipWithBounds>
              ) : null}
            </div>
          )
        }}
      </ParentSize>
    </div>
  )
}
