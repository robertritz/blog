export function formatMnt(value: number, digits = 0): string {
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value)
}

export function formatPercent(value: number, digits = 1): string {
  const sign = value > 0 ? "+" : ""
  return `${sign}${value.toFixed(digits)}%`
}

export function formatRatio(value: number): string {
  return `${value.toFixed(2)}x`
}

export function formatPeriod(period: string): string {
  const [year, month] = period.split("-")
  const date = new Date(Number(year), Number(month) - 1, 1)
  return date.toLocaleDateString("en-US", { year: "numeric", month: "short" })
}

export function periodToDate(period: string): Date {
  const [year, month] = period.split("-")
  return new Date(Date.UTC(Number(year), Number(month) - 1, 1))
}

export function clampNumber(
  value: number | null | undefined,
  fallback = 0,
): number {
  return Number.isFinite(value) ? Number(value) : fallback
}
