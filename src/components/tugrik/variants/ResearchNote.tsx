import { ForecastConeChart } from "../ForecastConeChart"
import { ForecastHistoryChart } from "../ForecastHistoryChart"
import {
  DriverStoryList,
  FactsRow,
  TrustFacts,
  TugrikPageHeading,
  type TugrikVariantProps,
} from "../shared"

export function ResearchNote({ model, onSelectHorizon }: TugrikVariantProps) {
  return (
    <article className="tugrik-variant tugrik-variant--research-note">
      <TugrikPageHeading model={model} onSelectHorizon={onSelectHorizon} />

      <section className="tugrik-section-block">
        <ForecastConeChart
          actual={model.charts.liveActual}
          forecastPoints={model.charts.liveForecast}
          selectedHorizon={model.selectedHorizon}
          annotationDensity="full"
          height="tall"
        />
        <FactsRow facts={model.facts} />
      </section>

      <hr className="tugrik-rule" />

      <section className="tugrik-section-block">
        <div className="tugrik-section-intro">
          <span className="tugrik-section-label">Trust</span>
          <h2>How the selected horizon has held up.</h2>
          <p>{model.trustLead}</p>
        </div>
        <TrustFacts facts={model.trustFacts} />
        <ForecastHistoryChart
          actualSeries={model.charts.historyActual}
          vintages={model.charts.historyVintages}
          selectedHorizon={model.selectedHorizon}
          recentWindowMonths={model.historyWindowMonths}
          height="standard"
          legendPlacement="bottom"
        />
      </section>

      <hr className="tugrik-rule" />

      <section className="tugrik-section-block">
        <div className="tugrik-section-intro">
          <span className="tugrik-section-label">Drivers</span>
          <h2>What seems to be moving the forecast.</h2>
          <p>{model.driverBullets[0]}</p>
        </div>
        <DriverStoryList stories={model.driverStories} />
      </section>
    </article>
  )
}
