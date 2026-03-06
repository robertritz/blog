import { ForecastConeChart } from "../ForecastConeChart"
import { ForecastHistoryChart } from "../ForecastHistoryChart"
import {
  DriverStoryList,
  FactsRow,
  MetaLine,
  TrustLines,
  type TugrikVariantProps,
} from "../shared"
import { HorizonToggle } from "../HorizonToggle"

export function WireSheet({ model, onSelectHorizon }: TugrikVariantProps) {
  return (
    <article className="tugrik-variant tugrik-variant--wire-sheet">
      <header className="tugrik-wire-head">
        <span className="tugrik-section-label">Wire Sheet</span>
        <h1>
          {model.headlineValue} by {model.headlinePeriod}
        </h1>
        <p>{model.wireDek}</p>
        <MetaLine model={model} compact />
        <div className="tugrik-heading-controls">
          <span className="tugrik-control-label">Forecast horizon</span>
          <HorizonToggle
            cards={model.cards}
            selectedHorizon={model.selectedHorizon}
            onSelect={onSelectHorizon}
          />
        </div>
      </header>

      <section className="tugrik-section-block">
        <ForecastConeChart
          actual={model.charts.liveActual}
          forecastPoints={model.charts.liveForecast}
          selectedHorizon={model.selectedHorizon}
          annotationDensity="minimal"
          height="standard"
        />
      </section>

      <section className="tugrik-wire-grid">
        <div>
          <span className="tugrik-section-label">Summary</span>
          <FactsRow facts={model.facts.slice(0, 3)} compact />
        </div>
        <div>
          <span className="tugrik-section-label">Trust</span>
          <TrustLines facts={model.trustFacts.slice(0, 4)} />
        </div>
      </section>

      <section className="tugrik-section-block">
        <ForecastHistoryChart
          actualSeries={model.charts.historyActual}
          vintages={model.charts.historyVintages}
          selectedHorizon={model.selectedHorizon}
          recentWindowMonths={model.historyWindowMonths}
          height="compact"
          legendPlacement="bottom"
        />
      </section>

      <section className="tugrik-section-block">
        <span className="tugrik-section-label">Drivers</span>
        <DriverStoryList stories={model.driverStories} mode="line" />
      </section>
    </article>
  )
}
