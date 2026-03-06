import { AxisBottom, AxisLeft } from "@visx/axis"
import { Group } from "@visx/group"
import { GridRows } from "@visx/grid"
import { ParentSize } from "@visx/responsive"
import { scaleLinear } from "@visx/scale"
import { LinePath } from "@visx/shape"
import type { TugrikComparisonRow } from "~/types/tugrik"

interface UsdCnyComparisonChartProps {
  rows: TugrikComparisonRow[]
}

export function UsdCnyComparisonChart({ rows }: UsdCnyComparisonChartProps) {
  return (
    <div className="tugrik-chart-surface tugrik-chart-surface--comparison">
      <ParentSize>
        {({ width, height }) => {
          const safeWidth = Math.max(width, 320)
          const safeHeight = Math.max(height, 320)
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
                  stroke="var(--tg-accent)"
                  strokeWidth={2.5}
                />
                <LinePath
                  data={rows}
                  x={(row) => xScale(row.horizon_months) ?? 0}
                  y={(row) => yScale(row.cny_champion_ratio) ?? 0}
                  stroke="var(--tg-green)"
                  strokeWidth={2.5}
                />
                {rows.map((row) => (
                  <g key={row.horizon_months}>
                    <circle
                      cx={xScale(row.horizon_months)}
                      cy={yScale(row.usd_champion_ratio)}
                      r={4.2}
                      fill="var(--tg-accent)"
                    />
                    <circle
                      cx={xScale(row.horizon_months)}
                      cy={yScale(row.cny_champion_ratio)}
                      r={4.2}
                      fill="var(--tg-green)"
                    />
                  </g>
                ))}
                <AxisLeft
                  scale={yScale}
                  numTicks={5}
                  stroke="var(--tg-grid-strong)"
                  tickStroke="var(--tg-grid-strong)"
                  tickLabelProps={() => ({
                    fill: "var(--tg-ink-muted)",
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
                    fill: "var(--tg-ink-muted)",
                    fontSize: 11,
                    textAnchor: "middle",
                  })}
                />
              </Group>
            </svg>
          )
        }}
      </ParentSize>
      <div className="tugrik-legend">
        <span>
          <i className="is-seeded" />
          USD/MNT champion
        </span>
        <span>
          <i className="is-published" />
          CNY/MNT champion
        </span>
      </div>
    </div>
  )
}
