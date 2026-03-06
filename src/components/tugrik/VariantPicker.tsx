import type {
  TugrikVariantDefinition,
  TugrikVariantId,
} from "./variant-registry"

interface VariantPickerProps {
  definitions: TugrikVariantDefinition[]
  selectedVariant: TugrikVariantId
  onSelect: (variant: TugrikVariantId) => void
}

export function VariantPicker({
  definitions,
  selectedVariant,
  onSelect,
}: VariantPickerProps) {
  const selectedDefinition =
    definitions.find((definition) => definition.id === selectedVariant) ??
    definitions[0]

  return (
    <div className="tugrik-variant-picker-block">
      <p className="tugrik-lab-note">Five live layouts, same data.</p>
      <div
        className="tugrik-variant-picker"
        role="tablist"
        aria-label="Choose tugrik layout variant"
      >
        {definitions.map((definition) => {
          const selected = definition.id === selectedVariant
          return (
            <button
              key={definition.id}
              type="button"
              role="tab"
              aria-selected={selected}
              className={`tugrik-variant-chip${selected ? "is-selected" : ""}`}
              title={definition.description}
              onClick={() => onSelect(definition.id)}
            >
              {definition.label}
            </button>
          )
        })}
      </div>
      <p className="tugrik-variant-caption">{selectedDefinition.description}</p>
    </div>
  )
}
