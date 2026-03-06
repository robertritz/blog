import type { ReactNode } from "react"

interface DisclosurePanelProps {
  title: string
  summary?: string
  children: ReactNode
}

export function DisclosurePanel({ title, summary, children }: DisclosurePanelProps) {
  return (
    <details className="tugrik-disclosure">
      <summary>
        <span>{title}</span>
        {summary ? <small>{summary}</small> : null}
      </summary>
      <div className="tugrik-disclosure-body">{children}</div>
    </details>
  )
}
