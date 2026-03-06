import type { TugrikForecastCard, TugrikHorizon } from "~/types/tugrik"

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
      className="tugrik-horizon-picker"
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
            className={`tugrik-horizon-chip${selected ? "is-selected" : ""}`}
            onClick={() => onSelect(card.horizon_months)}
          >
            {card.horizon_months}M
          </button>
        )
      })}
    </div>
  )
}
