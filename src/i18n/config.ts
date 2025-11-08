export const languages = {
  en: "English",
  mn: "Монгол",
} as const

export type Language = keyof typeof languages

export const defaultLang: Language = "en"

export const languageLabels: Record<Language, string> = {
  en: "English",
  mn: "Монгол",
}

export const locales: Record<Language, string> = {
  en: "en-US",
  mn: "mn-MN",
}

export function isValidLanguage(lang: string): lang is Language {
  return lang in languages
}
