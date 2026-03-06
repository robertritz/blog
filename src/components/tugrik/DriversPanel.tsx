import { AnimatePresence, motion } from "motion/react"
import type { TugrikDriverBucket, TugrikHorizon } from "~/types/tugrik"
import { DisclosurePanel } from "./DisclosurePanel"

interface DriversPanelProps {
  horizon: TugrikHorizon
  bucket: TugrikDriverBucket
  weakerExplainer: string
  strongerExplainer: string
}

export function DriversPanel({
  horizon,
  bucket,
  weakerExplainer,
  strongerExplainer,
}: DriversPanelProps) {
  return (
    <div className="tugrik-driver-layout">
      <AnimatePresence mode="wait">
        <motion.div
          key={`drivers-${horizon}`}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.22 }}
          className="tugrik-driver-columns"
        >
          <div className="tugrik-driver-column is-weaker">
            <header>
              <span className="tugrik-kicker">
                Pressure toward weaker tugrik
              </span>
              <p>{weakerExplainer}</p>
            </header>
            {bucket.positive.map((driver) => (
              <article key={driver.feature} className="tugrik-driver-card">
                <div className="tugrik-driver-head">
                  <strong>{driver.label}</strong>
                  <span>{Math.round(driver.stability * 100)}% stable</span>
                </div>
                <div className="tugrik-driver-bar">
                  <span
                    style={{
                      width: `${Math.max(driver.strength * 10000, 14)}%`,
                    }}
                  />
                </div>
                <p>{driver.interpretation}</p>
              </article>
            ))}
          </div>

          <div className="tugrik-driver-column is-stronger">
            <header>
              <span className="tugrik-kicker">
                Pressure toward stronger tugrik
              </span>
              <p>{strongerExplainer}</p>
            </header>
            {bucket.negative.map((driver) => (
              <article key={driver.feature} className="tugrik-driver-card">
                <div className="tugrik-driver-head">
                  <strong>{driver.label}</strong>
                  <span>{Math.round(driver.stability * 100)}% stable</span>
                </div>
                <div className="tugrik-driver-bar is-green">
                  <span
                    style={{
                      width: `${Math.max(driver.strength * 10000, 14)}%`,
                    }}
                  />
                </div>
                <p>{driver.interpretation}</p>
              </article>
            ))}
          </div>
        </motion.div>
      </AnimatePresence>

      <DisclosurePanel
        title="More model detail"
        summary="Best nonlinear signals for this horizon"
      >
        <div className="tugrik-tree-list">
          {bucket.tree.map((feature) => (
            <div key={feature.feature} className="tugrik-tree-row">
              <span>{feature.label}</span>
              <div className="tugrik-tree-bar">
                <span
                  style={{ width: `${feature.normalized_importance * 100}%` }}
                />
              </div>
              <small>{feature.family}</small>
            </div>
          ))}
        </div>
      </DisclosurePanel>
    </div>
  )
}
