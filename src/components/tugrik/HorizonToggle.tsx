import type { TugrikForecastCard, TugrikHorizon } from "~/types/tugrik"
import { formatMnt, formatPercent } from "./formatters"

interface HorizonToggleProps {
  cards: TugrikForecastCard[]
  selectedHorizon: TugrikHorizon
  onSelect: (horizon: TugrikHorizon) => void
}

export function HorizonToggle({
  cards,
  selectedHorizon,
  onSelect,
}: HorizonToggleProps) {
  return (
    <div
      className="tugrik-card-grid"
      role="tablist"
      aria-label="Forecast horizon"
    >
      {cards.map((card) => {
        const selected = card.horizon_months === selectedHorizon
        return (
          <button
            key={card.horizon_months}
            type="button"
            role="tab"
            aria-selected={selected}
            className={`tugrik-forecast-card${selected ? "is-selected" : ""}`}
            onClick={() => onSelect(card.horizon_months)}
          >
            <span className="tugrik-card-horizon">{card.horizon_months}M</span>
            <strong className="tugrik-card-value">
              {formatMnt(card.forecast_point)}
            </strong>
            <span className="tugrik-card-change">
              {formatPercent(card.pct_change_from_current, 2)}
            </span>
            <span className="tugrik-card-target">
              Target {card.target_period}
            </span>
          </button>
        )
      })}
    </div>
  )
}
