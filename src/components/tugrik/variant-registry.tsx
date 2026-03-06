import type { ComponentType } from "react"
import { ChartLedger } from "./variants/ChartLedger"
import { MarketsDesk } from "./variants/MarketsDesk"
import { ResearchNote } from "./variants/ResearchNote"
import { SplitBrief } from "./variants/SplitBrief"
import { WireSheet } from "./variants/WireSheet"
import type { TugrikVariantProps } from "./shared"

export type TugrikVariantId =
  | "research-note"
  | "markets-desk"
  | "split-brief"
  | "chart-ledger"
  | "wire-sheet"

export interface TugrikVariantDefinition {
  id: TugrikVariantId
  label: string
  description: string
  renderer: ComponentType<TugrikVariantProps>
}

export const DEFAULT_TUGRIK_VARIANT: TugrikVariantId = "research-note"

export const TUGRIK_VARIANTS: TugrikVariantDefinition[] = [
  {
    id: "research-note",
    label: "Research Note",
    description: "Calm single-column research page with the chart up front.",
    renderer: ResearchNote,
  },
  {
    id: "markets-desk",
    label: "Markets Desk",
    description: "Compact market-monitor layout with tighter stats.",
    renderer: MarketsDesk,
  },
  {
    id: "split-brief",
    label: "Split Brief",
    description:
      "Two-column memo with the chart on the left and notes on the right.",
    renderer: SplitBrief,
  },
  {
    id: "chart-ledger",
    label: "Chart Ledger",
    description: "Stacked charts with terse captions and very little prose.",
    renderer: ChartLedger,
  },
  {
    id: "wire-sheet",
    label: "Wire Sheet",
    description: "Lean wire-style sheet with terse bullets and stat lines.",
    renderer: WireSheet,
  },
]

export function isTugrikVariantId(
  value: string | null | undefined,
): value is TugrikVariantId {
  return TUGRIK_VARIANTS.some((definition) => definition.id === value)
}
