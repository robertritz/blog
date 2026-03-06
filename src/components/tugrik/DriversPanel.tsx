import { AnimatePresence, motion } from "motion/react"
import type {
  TugrikDriverBucket,
  TugrikDriverLinear,
  TugrikHorizon,
} from "~/types/tugrik"
import { DisclosurePanel } from "./DisclosurePanel"

interface DriversPanelProps {
  horizon: TugrikHorizon
  bucket: TugrikDriverBucket
  weakerExplainer: string
  strongerExplainer: string
}

interface DriverStory {
  key: string
  title: string
  direction: "weaker_tugrik" | "stronger_tugrik"
  summary: string
  sourceLabel: string
}

interface StoryDefinition {
  key: string
  title: string
  match: RegExp[]
  weakerSummary: string
  strongerSummary: string
}

const STORY_DEFINITIONS: StoryDefinition[] = [
  {
    key: "inflation",
    title: "Inflation pressure",
    match: [/inflation/i, /cpi/i],
    weakerSummary:
      "Higher inflation pressure usually lines up with a weaker tugrik later on.",
    strongerSummary:
      "Cooling inflation pressure usually gives the tugrik more room to hold firm.",
  },
  {
    key: "dollar_strength",
    title: "Global dollar strength",
    match: [/broad usd/i, /\busd index\b/i, /\bdxy\b/i],
    weakerSummary:
      "When the U.S. dollar strengthens broadly, USD/MNT usually drifts higher too.",
    strongerSummary:
      "When the global dollar backdrop softens, the tugrik usually gets some breathing room.",
  },
  {
    key: "trade_balance",
    title: "Trade balance",
    match: [/trade balance/i, /foreign trade/i],
    weakerSummary:
      "A softer trade position usually leaves the tugrik with less support.",
    strongerSummary: "A stronger trade position usually supports the tugrik.",
  },
  {
    key: "capital_flows",
    title: "Capital and external flows",
    match: [/financial account/i, /net errors/i, /reserve/i],
    weakerSummary:
      "Weaker external financing tends to leave the tugrik more exposed.",
    strongerSummary:
      "Stronger capital and external financing tends to cushion the tugrik.",
  },
  {
    key: "commodity_prices",
    title: "Commodity prices",
    match: [/coal/i, /copper/i, /gold/i, /brent/i, /oil/i],
    weakerSummary:
      "Softer export-price conditions can reduce foreign-currency inflows and weigh on the tugrik.",
    strongerSummary:
      "Better export-price conditions can support foreign-currency inflows and help the tugrik.",
  },
  {
    key: "china_link",
    title: "China-linked demand",
    match: [/cny/i, /neer/i],
    weakerSummary:
      "China-linked currency and demand signals can spill over into MNT pressure.",
    strongerSummary:
      "Healthier China-linked conditions can give the tugrik extra support.",
  },
]

export function DriversPanel({
  horizon,
  bucket,
  weakerExplainer,
  strongerExplainer,
}: DriversPanelProps) {
  const stories = buildStories(bucket)

  return (
    <div className="tugrik-driver-layout">
      <AnimatePresence mode="wait">
        <motion.div
          key={`drivers-${horizon}`}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.22 }}
          className="tugrik-story-grid"
        >
          {stories.map((story) => (
            <article
              key={story.key}
              className={`tugrik-story-card is-${story.direction}`}
            >
              <div className="tugrik-story-head">
                <span className="tugrik-story-badge">
                  {story.direction === "weaker_tugrik"
                    ? "Leans weaker tugrik"
                    : "Leans stronger tugrik"}
                </span>
                <strong>{story.title}</strong>
              </div>
              <p>{story.summary}</p>
              <small>Main signal now: {story.sourceLabel}</small>
            </article>
          ))}
        </motion.div>
      </AnimatePresence>

      <DisclosurePanel
        title="Model detail"
        summary="Raw features and nonlinear signals behind the stories"
      >
        <div className="tugrik-driver-detail-grid">
          <div className="tugrik-driver-detail-column">
            <strong>Raw features pushing toward weaker tugrik</strong>
            <p>{weakerExplainer}</p>
            <div className="tugrik-driver-detail-list">
              {bucket.positive.map((driver) => (
                <div key={driver.feature} className="tugrik-tree-row">
                  <span>{driver.label}</span>
                  <div className="tugrik-tree-bar">
                    <span
                      style={{
                        width: `${Math.max(driver.strength * 10000, 14)}%`,
                      }}
                    />
                  </div>
                  <small>{Math.round(driver.stability * 100)}% stable</small>
                </div>
              ))}
            </div>
          </div>

          <div className="tugrik-driver-detail-column">
            <strong>Raw features supporting the tugrik</strong>
            <p>{strongerExplainer}</p>
            <div className="tugrik-driver-detail-list">
              {bucket.negative.map((driver) => (
                <div key={driver.feature} className="tugrik-tree-row">
                  <span>{driver.label}</span>
                  <div className="tugrik-tree-bar">
                    <span
                      style={{
                        width: `${Math.max(driver.strength * 10000, 14)}%`,
                      }}
                    />
                  </div>
                  <small>{Math.round(driver.stability * 100)}% stable</small>
                </div>
              ))}
            </div>
          </div>
        </div>

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

function buildStories(bucket: TugrikDriverBucket): DriverStory[] {
  const strongestByStory = new Map<string, TugrikDriverLinear>()

  for (const driver of [...bucket.positive, ...bucket.negative]) {
    const definition = matchStory(driver)
    const existing = strongestByStory.get(definition.key)
    if (!existing || driver.strength > existing.strength) {
      strongestByStory.set(definition.key, driver)
    }
  }

  return Array.from(strongestByStory.values())
    .sort((a, b) => b.strength - a.strength)
    .slice(0, 4)
    .map((driver) => {
      const definition = matchStory(driver)
      return {
        key: definition.key,
        title: definition.title,
        direction: driver.direction,
        summary:
          driver.direction === "weaker_tugrik"
            ? definition.weakerSummary
            : definition.strongerSummary,
        sourceLabel: driver.label,
      }
    })
}

function matchStory(driver: TugrikDriverLinear): StoryDefinition {
  const haystack = `${driver.feature} ${driver.label}`.toLowerCase()
  return (
    STORY_DEFINITIONS.find((definition) =>
      definition.match.some((pattern) => pattern.test(haystack)),
    ) ?? {
      key: driver.feature,
      title: driver.label,
      match: [],
      weakerSummary: driver.interpretation,
      strongerSummary: driver.interpretation,
    }
  )
}
