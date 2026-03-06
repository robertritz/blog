import { AnimatePresence, motion, useReducedMotion } from "motion/react"
import { useEffect, useMemo, useState } from "react"
import type { TugrikDashboardData, TugrikHorizon } from "~/types/tugrik"
import { BottomPanels } from "./shared"
import { ResearchNote } from "./variants/ResearchNote"
import { buildTugrikViewModel } from "./view-model"

interface TugrikDashboardProps {
  data: TugrikDashboardData
}

/* ─────────────────────────────────────────────────────────
 * ANIMATION STORYBOARD
 *
 * Read top-to-bottom. Each `at` value is ms after mount.
 *
 *    0ms   research note fades into place
 *  120ms   supporting panels settle underneath
 * ───────────────────────────────────────────────────────── */

const TIMING = {
  content: 0, // lead research note appears
  panels: 120, // supporting panels settle in
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
      window.setTimeout(() => setStage(1), TIMING.content),
      window.setTimeout(() => setStage(2), TIMING.panels),
    ]
    return () => timers.forEach((timer) => window.clearTimeout(timer))
  }, [shouldReduceMotion])

  return (
    <div className="tugrik-dashboard">
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key="research-note"
          className="tugrik-variant-frame"
          initial={
            shouldReduceMotion ? false : { opacity: 0, y: stage >= 1 ? 0 : 8 }
          }
          animate={{ opacity: stage >= 1 ? 1 : 0, y: 0 }}
          exit={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: -6 }}
          transition={shouldReduceMotion ? { duration: 0 } : SHELL.fade}
        >
          <ResearchNote model={model} onSelectHorizon={setSelectedHorizon} />
        </motion.div>
      </AnimatePresence>

      <motion.div
        initial={{ opacity: 0, y: SHELL.offsetY }}
        animate={stage >= 2 ? { opacity: 1, y: 0 } : {}}
        transition={SHELL.spring}
      >
        <BottomPanels model={model} />
      </motion.div>
    </div>
  )
}
