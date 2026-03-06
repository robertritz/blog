import { AnimatePresence, motion, useReducedMotion } from "motion/react"
import { useEffect, useMemo, useState } from "react"
import type { TugrikDashboardData, TugrikHorizon } from "~/types/tugrik"
import { BottomPanels } from "./shared"
import { VariantPicker } from "./VariantPicker"
import {
  DEFAULT_TUGRIK_VARIANT,
  TUGRIK_VARIANTS,
  isTugrikVariantId,
  type TugrikVariantId,
} from "./variant-registry"
import { buildTugrikViewModel } from "./view-model"

interface TugrikDashboardProps {
  data: TugrikDashboardData
}

/* ─────────────────────────────────────────────────────────
 * ANIMATION STORYBOARD
 *
 * Read top-to-bottom. Each `at` value is ms after mount.
 *
 *    0ms   lab note appears
 *   80ms   variant picker settles in
 *  160ms   selected layout fades into place
 * ───────────────────────────────────────────────────────── */

const TIMING = {
  labNote: 0, // lab note and picker container appear
  controls: 80, // picker settles in
  content: 160, // main variant content fades in
}

const SHELL = {
  offsetY: 10, // light upward travel on entry
  spring: { type: "spring" as const, stiffness: 280, damping: 30 },
  fade: { duration: 0.16 },
}

export function TugrikDashboard({ data }: TugrikDashboardProps) {
  const shouldReduceMotion = useReducedMotion()
  const [stage, setStage] = useState(0)
  const [selectedHorizon, setSelectedHorizon] = useState<TugrikHorizon>(
    data.summary.default_horizon,
  )
  const [selectedVariant, setSelectedVariant] = useState<TugrikVariantId>(
    DEFAULT_TUGRIK_VARIANT,
  )

  const selectedDefinition =
    TUGRIK_VARIANTS.find((definition) => definition.id === selectedVariant) ??
    TUGRIK_VARIANTS[0]
  const VariantRenderer = selectedDefinition.renderer

  const model = useMemo(
    () => buildTugrikViewModel(data, selectedHorizon),
    [data, selectedHorizon],
  )

  useEffect(() => {
    if (shouldReduceMotion) {
      setStage(3)
      return
    }

    setStage(0)
    const timers = [
      window.setTimeout(() => setStage(1), TIMING.labNote),
      window.setTimeout(() => setStage(2), TIMING.controls),
      window.setTimeout(() => setStage(3), TIMING.content),
    ]
    return () => timers.forEach((timer) => window.clearTimeout(timer))
  }, [shouldReduceMotion])

  useEffect(() => {
    if (typeof window === "undefined") {
      return
    }

    setSelectedVariant(normalizeVariantInUrl())

    const handlePopState = () => {
      setSelectedVariant(readVariantFromLocation(window.location.search))
    }

    window.addEventListener("popstate", handlePopState)
    return () => window.removeEventListener("popstate", handlePopState)
  }, [])

  const handleVariantChange = (variant: TugrikVariantId) => {
    setSelectedVariant(variant)

    if (typeof window === "undefined") {
      return
    }

    const url = new URL(window.location.href)
    if (variant === DEFAULT_TUGRIK_VARIANT) {
      url.searchParams.delete("view")
    } else {
      url.searchParams.set("view", variant)
    }

    window.history.pushState({ view: variant }, "", url)
  }

  return (
    <div className="tugrik-dashboard">
      <motion.div
        className="tugrik-lab-controls"
        initial={{ opacity: 0, y: SHELL.offsetY }}
        animate={stage >= 2 ? { opacity: 1, y: 0 } : {}}
        transition={SHELL.spring}
      >
        <VariantPicker
          definitions={TUGRIK_VARIANTS}
          selectedVariant={selectedVariant}
          onSelect={handleVariantChange}
        />
      </motion.div>

      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={selectedVariant}
          className="tugrik-variant-frame"
          initial={
            shouldReduceMotion ? false : { opacity: 0, y: stage >= 3 ? 0 : 8 }
          }
          animate={{ opacity: stage >= 3 ? 1 : 0, y: 0 }}
          exit={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: -6 }}
          transition={shouldReduceMotion ? { duration: 0 } : SHELL.fade}
        >
          <VariantRenderer model={model} onSelectHorizon={setSelectedHorizon} />
        </motion.div>
      </AnimatePresence>

      <motion.div
        initial={{ opacity: 0, y: SHELL.offsetY }}
        animate={stage >= 3 ? { opacity: 1, y: 0 } : {}}
        transition={SHELL.spring}
      >
        <BottomPanels model={model} />
      </motion.div>
    </div>
  )
}

function readVariantFromLocation(search?: string): TugrikVariantId {
  if (typeof window === "undefined" && !search) {
    return DEFAULT_TUGRIK_VARIANT
  }

  const params = new URLSearchParams(search ?? window.location.search)
  const rawVariant = params.get("view")
  return isTugrikVariantId(rawVariant) ? rawVariant : DEFAULT_TUGRIK_VARIANT
}

function normalizeVariantInUrl(): TugrikVariantId {
  const url = new URL(window.location.href)
  const rawVariant = url.searchParams.get("view")

  if (!rawVariant) {
    return DEFAULT_TUGRIK_VARIANT
  }

  if (isTugrikVariantId(rawVariant)) {
    return rawVariant
  }

  url.searchParams.delete("view")
  window.history.replaceState({ view: DEFAULT_TUGRIK_VARIANT }, "", url)
  return DEFAULT_TUGRIK_VARIANT
}
