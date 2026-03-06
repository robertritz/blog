import { AxisBottom, AxisLeft } from "@visx/axis"
import { Group } from "@visx/group"
import { GridRows } from "@visx/grid"
import { ParentSize } from "@visx/responsive"
import { scaleLinear } from "@visx/scale"
import { LinePath } from "@visx/shape"
import type { TugrikComparisonRow } from "~/types/tugrik"

type TugrikChartHeight = "compact" | "standard" | "tall"

interface UsdCnyComparisonChartProps {
  rows: TugrikComparisonRow[]
  framed?: boolean
  height?: TugrikChartHeight
  legendPlacement?: "top" | "bottom" | "none"
}

export function UsdCnyComparisonChart({
  rows,
  framed = false,
  height = "standard",
  legendPlacement = "bottom",
}: UsdCnyComparisonChartProps) {
  return (
    <div
      className={`tugrik-chart-surface ${framed ? "is-framed" : "is-plain"}`}
    >
      {legendPlacement === "top" ? <ComparisonLegend /> : null}

      <div className={`tugrik-chart-canvas is-${height}`}>
        <ParentSize>
          {({ width, height: canvasHeight }) => {
            const safeWidth = Math.max(width, 320)
            const safeHeight = Math.max(
              canvasHeight,
              getMinimumChartHeight(height),
            )
            const margin = { top: 20, right: 16, bottom: 36, left: 52 }
            const innerWidth = safeWidth - margin.left - margin.right
            const innerHeight = safeHeight - margin.top - margin.bottom
            const xScale = scaleLinear({
              domain: [1, 12],
              range: [0, innerWidth],
            })
            const yScale = scaleLinear({
              domain: [
                0,
                Math.max(
                  1.1,
                  ...rows.flatMap((row) => [
                    row.usd_champion_ratio,
                    row.cny_champion_ratio,
                  ]),
                ),
              ],
              range: [innerHeight, 0],
              nice: true,
            })

            return (
              <svg
                width={safeWidth}
                height={safeHeight}
                role="img"
                aria-label="USD and CNY forecast performance against random walk"
              >
                <Group left={margin.left} top={margin.top}>
                  <GridRows
                    scale={yScale}
                    width={innerWidth}
                    stroke="var(--tg-grid)"
                  />
                  <line
                    x1={0}
                    x2={innerWidth}
                    y1={yScale(1)}
                    y2={yScale(1)}
                    stroke="var(--tg-grid-strong)"
                    strokeDasharray="5 4"
                  />

                  <LinePath
                    data={rows}
                    x={(row) => xScale(row.horizon_months) ?? 0}
                    y={(row) => yScale(row.usd_champion_ratio) ?? 0}
                    stroke="var(--tg-series-forecast)"
                    strokeWidth={2.4}
                  />
                  <LinePath
                    data={rows}
                    x={(row) => xScale(row.horizon_months) ?? 0}
                    y={(row) => yScale(row.cny_champion_ratio) ?? 0}
                    stroke="var(--tg-series-benchmark)"
                    strokeWidth={2.4}
                  />

                  {rows.map((row) => (
                    <g key={row.horizon_months}>
                      <circle
                        cx={xScale(row.horizon_months)}
                        cy={yScale(row.usd_champion_ratio)}
                        r={4}
                        fill="var(--tg-series-forecast)"
                      />
                      <circle
                        cx={xScale(row.horizon_months)}
                        cy={yScale(row.cny_champion_ratio)}
                        r={4}
                        fill="var(--tg-series-benchmark)"
                      />
                    </g>
                  ))}

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
                  />

                  <AxisBottom
                    top={innerHeight}
                    scale={xScale}
                    tickValues={[1, 3, 6, 12]}
                    stroke="var(--tg-grid-strong)"
                    tickStroke="var(--tg-grid-strong)"
                    tickLabelProps={() => ({
                      fill: "var(--tg-text-muted)",
                      fontSize: 11,
                      textAnchor: "middle",
                    })}
                  />
                </Group>
              </svg>
            )
          }}
        </ParentSize>
      </div>

      {legendPlacement === "bottom" ? <ComparisonLegend /> : null}
    </div>
  )
}

function ComparisonLegend() {
  return (
    <div className="tugrik-legend">
      <span>
        <i className="is-forecast" />
        USD/MNT champion
      </span>
      <span>
        <i className="is-benchmark" />
        CNY/MNT champion
      </span>
    </div>
  )
}

function getMinimumChartHeight(height: TugrikChartHeight) {
  if (height === "compact") {
    return 280
  }

  if (height === "tall") {
    return 360
  }

  return 320
}
