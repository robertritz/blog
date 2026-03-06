import { useState } from "react"
import type { TugrikForecastCard } from "~/types/tugrik"
import { ForecastConeChart } from "./ForecastConeChart"
import { formatMnt, formatPeriod } from "./formatters"
import { FactsRow } from "./shared"
import type {
  TugrikDashboardViewModel,
  TugrikFactItem,
  TugrikScenarioInput,
} from "./view-model"

type ScenarioTilt = -1 | 0 | 1

interface ScenarioWorkbenchProps {
  model: TugrikDashboardViewModel
}

interface ScenarioSummary {
  activeAssumptions: string[]
  facts: TugrikFactItem[]
  forecastPoints: TugrikForecastCard[]
  message: string
}

const SCENARIO_OPTIONS: Array<{ value: ScenarioTilt; label: string }> = [
  { value: -1, label: "Lower" },
  { value: 0, label: "Base" },
  { value: 1, label: "Higher" },
]

export function ScenarioWorkbench({ model }: ScenarioWorkbenchProps) {
  const [scenarioState, setScenarioState] = useState<
    Record<string, ScenarioTilt | undefined>
  >({})

  if (!model.scenarioInputs.length) {
    return null
  }

  const totalScenarioWeight = model.scenarioInputs.reduce(
    (sum, input) => sum + input.scenarioWeight,
    0,
  )
  const summary = buildScenarioSummary(model, scenarioState)
  const hasScenario = summary.activeAssumptions.length > 0

  return (
    <div className="tugrik-scenario-workbench">
      <div className="tugrik-scenario-toolbar">
        <p className="tugrik-scenario-message">{summary.message}</p>
        <button
          type="button"
          className={hasScenario ? "tugrik-chip is-selected" : "tugrik-chip"}
          onClick={() => setScenarioState({})}
          disabled={!hasScenario}
        >
          Reset scenario
        </button>
      </div>

      <div className="tugrik-scenario-control-grid">
        {model.scenarioInputs.map((input) => {
          const selectedTilt = scenarioState[input.feature] ?? 0
          const weightShare =
            totalScenarioWeight > 0
              ? Math.round((input.scenarioWeight / totalScenarioWeight) * 100)
              : 0

          return (
            <article key={input.feature} className="tugrik-scenario-card">
              <div className="tugrik-scenario-card-head">
                <div>
                  <strong>{input.label}</strong>
                  <small>{weightShare}% of the live scenario mix</small>
                </div>
                <span className="tugrik-scenario-card-tone">
                  {input.direction === "weaker_tugrik"
                    ? "Higher usually lifts USD/MNT"
                    : "Higher usually lowers USD/MNT"}
                </span>
              </div>

              <div className="tugrik-chip-row">
                {SCENARIO_OPTIONS.map((option) => (
                  <button
                    key={option.label}
                    type="button"
                    className={
                      selectedTilt === option.value
                        ? "tugrik-chip is-selected"
                        : "tugrik-chip"
                    }
                    onClick={() =>
                      setScenarioState((current) => ({
                        ...current,
                        [input.feature]: option.value,
                      }))
                    }
                  >
                    {option.label}
                  </button>
                ))}
              </div>

              <p className="tugrik-scenario-card-copy">
                {buildScenarioInterpretation(input)}
              </p>
            </article>
          )
        })}
      </div>

      <div className="tugrik-scenario-output">
        <ForecastConeChart
          actual={model.charts.liveActual}
          forecastPoints={summary.forecastPoints}
          selectedHorizon={model.selectedHorizon}
          annotationDensity="minimal"
          height="standard"
        />
        <FactsRow facts={summary.facts} compact />
        {summary.activeAssumptions.length ? (
          <div className="tugrik-scenario-assumptions">
            {summary.activeAssumptions.map((assumption) => (
              <span key={assumption} className="tugrik-scenario-assumption">
                {assumption}
              </span>
            ))}
          </div>
        ) : null}
        <p className="tugrik-scenario-note">
          Illustrative only. This client-side tool nudges the published forecast
          along the strongest current inputs and widens the bands a bit under
          larger shocks. It is not a full model rerun.
        </p>
      </div>
    </div>
  )
}

function buildScenarioSummary(
  model: TugrikDashboardViewModel,
  scenarioState: Record<string, ScenarioTilt | undefined>,
): ScenarioSummary {
  const totalScenarioWeight = model.scenarioInputs.reduce(
    (sum, input) => sum + input.scenarioWeight,
    0,
  )
  const normalizedPressure =
    totalScenarioWeight > 0
      ? model.scenarioInputs.reduce((sum, input) => {
          const tilt = scenarioState[input.feature] ?? 0
          const directionWeight = input.direction === "weaker_tugrik" ? 1 : -1
          return sum + tilt * directionWeight * input.scenarioWeight
        }, 0) / totalScenarioWeight
      : 0
  const scenarioShiftMnt = normalizedPressure * getScenarioBudget(model)
  const scenarioForecast = model.charts.liveForecast.map((point) =>
    buildScenarioPoint(
      point,
      scenarioShiftMnt,
      normalizedPressure,
      model.selectedHorizon,
    ),
  )
  const selectedScenarioPoint =
    scenarioForecast.find(
      (point) => point.horizon_months === model.selectedHorizon,
    ) ?? scenarioForecast[0]
  const activeAssumptions = model.scenarioInputs.flatMap((input) => {
    const tilt = scenarioState[input.feature] ?? 0
    if (tilt === 0) {
      return []
    }

    return [`${tilt > 0 ? "Higher" : "Lower"} ${input.label}`]
  })
  const facts = buildScenarioFacts(
    selectedScenarioPoint,
    scenarioShiftMnt,
    activeAssumptions.length,
  )

  if (!activeAssumptions.length) {
    return {
      activeAssumptions,
      facts,
      forecastPoints: scenarioForecast,
      message: `Base case unchanged. Move the strongest live inputs up or down to pressure-test the ${model.selectedHorizon}M path without leaving the page.`,
    }
  }

  const directionLabel =
    scenarioShiftMnt > 0 ? "toward a weaker tugrik" : "toward a stronger tugrik"
  const absoluteShift = Math.abs(scenarioShiftMnt)

  return {
    activeAssumptions,
    facts,
    forecastPoints: scenarioForecast,
    message: `This mix shifts the ${model.selectedHorizon}M case ${formatMnt(absoluteShift, 1)} MNT ${scenarioShiftMnt > 0 ? "higher" : "lower"}, ${directionLabel}: ${formatMnt(selectedScenarioPoint.forecast_point, 1)} by ${formatPeriod(selectedScenarioPoint.target_period)}.`,
  }
}

function buildScenarioFacts(
  selectedScenarioPoint: TugrikForecastCard,
  scenarioShiftMnt: number,
  activeAssumptionCount: number,
): TugrikFactItem[] {
  return [
    {
      label: "Scenario case",
      value: `${formatMnt(selectedScenarioPoint.forecast_point, 1)} by ${formatPeriod(selectedScenarioPoint.target_period)}`,
    },
    {
      label: "Vs base case",
      value: `${formatSignedMnt(scenarioShiftMnt, 1)} MNT`,
    },
    {
      label: "80% range",
      value: `${formatMnt(selectedScenarioPoint.interval80_lo, 1)} to ${formatMnt(selectedScenarioPoint.interval80_hi, 1)}`,
    },
    {
      label: "Inputs moved",
      value:
        activeAssumptionCount > 0
          ? `${activeAssumptionCount} ${activeAssumptionCount === 1 ? "input" : "inputs"}`
          : "0 inputs",
    },
  ]
}

function buildScenarioPoint(
  point: TugrikForecastCard,
  scenarioShiftMnt: number,
  normalizedPressure: number,
  selectedHorizon: TugrikDashboardViewModel["selectedHorizon"],
): TugrikForecastCard {
  const ramp = getScenarioRamp(point.horizon_months, selectedHorizon)
  const uncertaintyFactor = 1 + Math.abs(normalizedPressure) * 0.18 * ramp
  const shiftedForecastPoint = point.forecast_point + scenarioShiftMnt * ramp
  const lower80Distance =
    (point.forecast_point - point.interval80_lo) * uncertaintyFactor
  const upper80Distance =
    (point.interval80_hi - point.forecast_point) * uncertaintyFactor
  const lower95Distance =
    (point.forecast_point - point.interval95_lo) * uncertaintyFactor
  const upper95Distance =
    (point.interval95_hi - point.forecast_point) * uncertaintyFactor

  return {
    ...point,
    forecast_point: shiftedForecastPoint,
    interval80_lo: shiftedForecastPoint - lower80Distance,
    interval80_hi: shiftedForecastPoint + upper80Distance,
    interval95_lo: shiftedForecastPoint - lower95Distance,
    interval95_hi: shiftedForecastPoint + upper95Distance,
    ensemble_mean: point.ensemble_mean + scenarioShiftMnt * ramp,
    ensemble_min: point.ensemble_min + scenarioShiftMnt * ramp,
    ensemble_max: point.ensemble_max + scenarioShiftMnt * ramp,
    pct_change_from_current:
      ((shiftedForecastPoint - point.current_level) / point.current_level) *
      100,
  }
}

function getScenarioBudget(model: TugrikDashboardViewModel) {
  const bandWidth =
    model.selectedCard.interval80_hi - model.selectedCard.interval80_lo
  return Math.min(Math.max(bandWidth * 0.72, 18), 130)
}

function getScenarioRamp(
  horizonMonths: TugrikForecastCard["horizon_months"],
  selectedHorizon: TugrikDashboardViewModel["selectedHorizon"],
) {
  const relativeRamp = horizonMonths / selectedHorizon
  return Math.max(0.35, Math.min(relativeRamp, 1.15))
}

function buildScenarioInterpretation(input: TugrikScenarioInput) {
  const cleanerInterpretation = input.interpretation.replace(/\s+/g, " ").trim()
  const stabilityLabel =
    input.stability >= 0.8
      ? "Shows up consistently in the current run."
      : "Shows up, but with a looser signal than the top inputs."

  return `${cleanerInterpretation} ${stabilityLabel}`
}

function formatSignedMnt(value: number, digits = 0) {
  const sign = value > 0 ? "+" : ""
  return `${sign}${formatMnt(value, digits)}`
}
