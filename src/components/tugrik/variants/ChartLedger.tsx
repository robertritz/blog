import { ForecastConeChart } from "../ForecastConeChart"
import { ForecastHistoryChart } from "../ForecastHistoryChart"
import { TrustLines, type TugrikVariantProps } from "../shared"
import { HorizonToggle } from "../HorizonToggle"

export function ChartLedger({ model, onSelectHorizon }: TugrikVariantProps) {
  return (
    <article className="tugrik-variant tugrik-variant--chart-ledger">
      <header className="tugrik-ledger-head">
        <div>
          <span className="tugrik-section-label">Chart Ledger</span>
          <h1>{model.pageTitle}</h1>
          <p>{model.wireDek}</p>
        </div>
        <div className="tugrik-heading-controls">
          <span className="tugrik-control-label">Forecast horizon</span>
          <HorizonToggle
            cards={model.cards}
            selectedHorizon={model.selectedHorizon}
            onSelect={onSelectHorizon}
          />
        </div>
      </header>

      <section className="tugrik-ledger-stack">
        <div className="tugrik-ledger-chart">
          <span className="tugrik-section-label">Live forecast</span>
          <ForecastConeChart
            actual={model.charts.liveActual}
            forecastPoints={model.charts.liveForecast}
            selectedHorizon={model.selectedHorizon}
            annotationDensity="minimal"
            height="compact"
          />
        </div>

        <div className="tugrik-ledger-chart">
          <span className="tugrik-section-label">Forecast vs actual</span>
          <ForecastHistoryChart
            actualSeries={model.charts.historyActual}
            vintages={model.charts.historyVintages}
            selectedHorizon={model.selectedHorizon}
            recentWindowMonths={model.historyWindowMonths}
            height="compact"
            legendPlacement="top"
            showWindowControls={false}
          />
        </div>
      </section>

      <section className="tugrik-ledger-grid">
        <div>
          <span className="tugrik-section-label">Numbers</span>
          <TrustLines facts={model.facts.slice(0, 4)} />
        </div>
        <div>
          <span className="tugrik-section-label">Trust</span>
          <TrustLines facts={model.trustFacts.slice(0, 4)} />
        </div>
        <div>
          <span className="tugrik-section-label">Drivers</span>
          <ul className="tugrik-driver-text-list">
            {model.driverLines.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
      </section>
    </article>
  )
}
