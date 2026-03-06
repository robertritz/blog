import type { TugrikHorizon } from "~/types/tugrik"
import { DisclosurePanel } from "./DisclosurePanel"
import { HorizonToggle } from "./HorizonToggle"
import { UsdCnyComparisonChart } from "./UsdCnyComparisonChart"
import type { TugrikDashboardViewModel } from "./view-model"

export interface TugrikVariantProps {
  model: TugrikDashboardViewModel
  onSelectHorizon: (horizon: TugrikHorizon) => void
}

interface MetaLineProps {
  model: TugrikDashboardViewModel
  compact?: boolean
}

interface FactsRowProps {
  facts: TugrikDashboardViewModel["facts"]
  compact?: boolean
}

interface TrustFactsProps {
  facts: TugrikDashboardViewModel["trustFacts"]
}

interface StoryListProps {
  stories: TugrikDashboardViewModel["driverStories"]
  mode?: "bullet" | "line"
}

export function TugrikPageHeading({
  model,
  onSelectHorizon,
  compact = false,
}: TugrikVariantProps & { compact?: boolean }) {
  return (
    <header
      className={
        compact ? "tugrik-page-heading is-compact" : "tugrik-page-heading"
      }
    >
      <div className="tugrik-page-heading-copy">
        <h1>{model.pageTitle}</h1>
        <p>{model.pageDeck}</p>
      </div>
      <MetaLine model={model} compact={compact} />
      <div className="tugrik-heading-controls">
        <span className="tugrik-control-label">Forecast horizon</span>
        <HorizonToggle
          cards={model.cards}
          selectedHorizon={model.selectedHorizon}
          onSelect={onSelectHorizon}
        />
      </div>
    </header>
  )
}

export function MetaLine({ model, compact = false }: MetaLineProps) {
  return (
    <div
      className={compact ? "tugrik-meta-line is-compact" : "tugrik-meta-line"}
    >
      <span>{model.asOfLine}</span>
      <span>Aligned now {model.currentLevel}</span>
    </div>
  )
}

export function FactsRow({ facts, compact = false }: FactsRowProps) {
  return (
    <dl
      className={compact ? "tugrik-facts-row is-compact" : "tugrik-facts-row"}
    >
      {facts.map((fact) => (
        <div key={fact.label}>
          <dt>{fact.label}</dt>
          <dd>{fact.value}</dd>
        </div>
      ))}
    </dl>
  )
}

export function TrustFacts({ facts }: TrustFactsProps) {
  return (
    <dl className="tugrik-trust-facts">
      {facts.map((fact) => (
        <div key={fact.label}>
          <dt>{fact.label}</dt>
          <dd>{fact.value}</dd>
        </div>
      ))}
    </dl>
  )
}

export function TrustLines({ facts }: TrustFactsProps) {
  return (
    <ul className="tugrik-stat-lines">
      {facts.map((fact) => (
        <li key={fact.label}>
          <span>{fact.label}</span>
          <strong>{fact.value}</strong>
        </li>
      ))}
    </ul>
  )
}

export function DriverStoryList({ stories, mode = "bullet" }: StoryListProps) {
  if (mode === "line") {
    return (
      <ul className="tugrik-driver-lines">
        {stories.map((story) => (
          <li key={story.key}>
            <strong>{story.title}</strong>
            <span>
              {story.direction === "weaker_tugrik"
                ? "Leans weaker tugrik"
                : "Supports the tugrik"}
            </span>
            <p>{story.summary}</p>
          </li>
        ))}
      </ul>
    )
  }

  return (
    <ul className="tugrik-driver-bullets">
      {stories.map((story) => (
        <li key={story.key}>
          <strong>{story.title}.</strong> {story.summary}
        </li>
      ))}
    </ul>
  )
}

export function BottomPanels({ model }: { model: TugrikDashboardViewModel }) {
  return (
    <section className="tugrik-bottom-panels" aria-label="Method and data">
      <DisclosurePanel
        title="Method"
        summary="How the forecast is produced and how to read it"
      >
        <ul className="tugrik-panel-bullets">
          {model.methodBullets.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </DisclosurePanel>

      <DisclosurePanel
        title="Freshness"
        summary="Update timing across the underlying inputs"
      >
        <div className="tugrik-source-list">
          {model.sourceUpdates.map((source) => (
            <div key={source.key} className="tugrik-source-row">
              <strong>{source.label}</strong>
              <span>{source.lastPeriod}</span>
              <small>Updated {source.updatedAt}</small>
            </div>
          ))}
        </div>
      </DisclosurePanel>

      <DisclosurePanel
        title="Raw signals & USD/CNY"
        summary="Underlying features and the comparison benchmark"
      >
        <div className="tugrik-panel-stack">
          <p className="tugrik-panel-copy">{model.comparisonTakeaway}</p>
          <UsdCnyComparisonChart
            rows={model.charts.comparisonRows}
            framed
            height="compact"
            legendPlacement="bottom"
          />
          <div className="tugrik-raw-grid">
            <section>
              <h3>Signals pushing toward weaker tugrik</h3>
              <p>{model.rawExplainers.weaker}</p>
              <div className="tugrik-raw-list">
                {model.weakerSignals.map((signal) => (
                  <div key={signal.feature} className="tugrik-raw-row">
                    <span>{signal.label}</span>
                    <small>{Math.round(signal.stability * 100)}% stable</small>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3>Signals supporting the tugrik</h3>
              <p>{model.rawExplainers.stronger}</p>
              <div className="tugrik-raw-list">
                {model.strongerSignals.map((signal) => (
                  <div key={signal.feature} className="tugrik-raw-row">
                    <span>{signal.label}</span>
                    <small>{Math.round(signal.stability * 100)}% stable</small>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="tugrik-tree-list">
            {model.treeSignals.map((signal) => (
              <div key={signal.feature} className="tugrik-tree-row">
                <span>{signal.label}</span>
                <div className="tugrik-tree-bar">
                  <span
                    style={{
                      width: `${Math.max(signal.normalized_importance * 100, 10)}%`,
                    }}
                  />
                </div>
                <small>{signal.family}</small>
              </div>
            ))}
          </div>
        </div>
      </DisclosurePanel>

      <DisclosurePanel title="Downloads" summary="Public artifacts for reuse">
        <div className="tugrik-download-list">
          {model.downloads.map((item) => (
            <a key={item.label} href={item.href}>
              {item.label}
            </a>
          ))}
        </div>
      </DisclosurePanel>
    </section>
  )
}
