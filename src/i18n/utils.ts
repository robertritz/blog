import type { Language } from "./config"
import { defaultLang, locales } from "./config"

import enTranslations from "./translations/en.json"
import mnTranslations from "./translations/mn.json"

const translations = {
  en: enTranslations,
  mn: mnTranslations,
}

export function getTranslations(lang: Language) {
  return translations[lang] || translations[defaultLang]
}

export function t(key: string, lang: Language): string {
  const keys = key.split(".")
  const trans = getTranslations(lang)

  let value: any = trans
  for (const k of keys) {
    value = value?.[k]
    if (value === undefined) {
      console.warn(`Translation key not found: ${key} for language: ${lang}`)
      return key
    }
  }

  return typeof value === "string" ? value : key
}

export function getLocalizedPath(path: string, lang: Language): string {
  // Remove leading slash if present
  const cleanPath = path.startsWith("/") ? path.slice(1) : path

  // Add language prefix
  return `/${lang}/${cleanPath}`
}

export function getLocale(lang: Language): string {
  return locales[lang] || locales[defaultLang]
}

export function getOtherLanguage(currentLang: Language): Language {
  return currentLang === "en" ? "mn" : "en"
}
