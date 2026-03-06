import { ForecastConeChart } from "../ForecastConeChart"
import { ForecastHistoryChart } from "../ForecastHistoryChart"
import {
  DriverStoryList,
  MetaLine,
  TrustFacts,
  type TugrikVariantProps,
} from "../shared"
import { HorizonToggle } from "../HorizonToggle"

export function MarketsDesk({ model, onSelectHorizon }: TugrikVariantProps) {
  return (
    <article className="tugrik-variant tugrik-variant--markets-desk">
      <section className="tugrik-markets-strip">
        <div>
          <span className="tugrik-section-label">Markets Desk</span>
          <h1>
            {model.headlineValue} <small>by {model.headlinePeriod}</small>
          </h1>
        </div>
        <div className="tugrik-markets-strip-stats">
          <div>
            <span>Change</span>
            <strong>{model.changeFromCurrent}</strong>
          </div>
          <div>
            <span>Freshness</span>
            <strong>{model.freshnessLabel}</strong>
          </div>
          <div>
            <span>As of</span>
            <strong>{model.alignedPeriod}</strong>
          </div>
        </div>
      </section>

      <MetaLine model={model} compact />

      <div className="tugrik-heading-controls">
        <span className="tugrik-control-label">Forecast horizon</span>
        <HorizonToggle
          cards={model.cards}
          selectedHorizon={model.selectedHorizon}
          onSelect={onSelectHorizon}
        />
      </div>

      <section className="tugrik-desk-grid">
        <div className="tugrik-desk-main">
          <ForecastConeChart
            actual={model.charts.liveActual}
            forecastPoints={model.charts.liveForecast}
            selectedHorizon={model.selectedHorizon}
            annotationDensity="minimal"
            height="standard"
          />
        </div>

        <aside className="tugrik-side-note">
          <span className="tugrik-section-label">Trust</span>
          <p className="tugrik-tight-copy">{model.trustLead}</p>
          <TrustFacts facts={model.trustFacts.slice(0, 4)} />
        </aside>
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
        <DriverStoryList stories={model.driverStories} />
      </section>
    </article>
  )
}
