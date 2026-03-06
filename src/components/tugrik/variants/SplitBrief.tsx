import { ForecastConeChart } from "../ForecastConeChart"
import { ForecastHistoryChart } from "../ForecastHistoryChart"
import {
  DriverStoryList,
  FactsRow,
  MetaLine,
  TrustFacts,
  TugrikPageHeading,
  type TugrikVariantProps,
} from "../shared"

export function SplitBrief({ model, onSelectHorizon }: TugrikVariantProps) {
  return (
    <article className="tugrik-variant tugrik-variant--split-brief">
      <div className="tugrik-split-grid">
        <div className="tugrik-split-main">
          <TugrikPageHeading
            model={model}
            onSelectHorizon={onSelectHorizon}
            compact
          />
          <ForecastConeChart
            actual={model.charts.liveActual}
            forecastPoints={model.charts.liveForecast}
            selectedHorizon={model.selectedHorizon}
            annotationDensity="minimal"
            height="standard"
          />
        </div>

        <aside className="tugrik-side-note">
          <MetaLine model={model} compact />
          <FactsRow facts={model.facts} compact />
          <div className="tugrik-side-section">
            <span className="tugrik-section-label">Trust</span>
            <p className="tugrik-tight-copy">{model.trustLead}</p>
            <TrustFacts facts={model.trustFacts.slice(0, 4)} />
          </div>
          <div className="tugrik-side-section">
            <span className="tugrik-section-label">Top drivers</span>
            <DriverStoryList stories={model.driverStories} />
          </div>
        </aside>
      </div>

      <section className="tugrik-section-block">
        <ForecastHistoryChart
          actualSeries={model.charts.historyActual}
          vintages={model.charts.historyVintages}
          selectedHorizon={model.selectedHorizon}
          recentWindowMonths={model.historyWindowMonths}
          height="standard"
          legendPlacement="bottom"
        />
      </section>
    </article>
  )
}
