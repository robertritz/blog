import { Languages } from "lucide-react"

export function LanguageToggle() {
  const handleLanguageToggle = () => {
    const currentPath = window.location.pathname
    const currentLang = currentPath.includes("/en") ? "en" : "mn"
    const targetLang = currentLang === "en" ? "mn" : "en"

    // If we're on a post page
    if (currentPath.includes("/posts/")) {
      // Find the article element that contains our translation URLs
      const article = document.querySelector('article[data-en-url], article[data-mn-url]')
      if (article) {
        const translationUrl = article.getAttribute(`data-${targetLang}-url`)
        if (translationUrl) {
          window.location.href = translationUrl
          return
        }
      }
    }

    // Default behavior for non-post pages
    const newPath = currentPath.replace(`/${currentLang}`, `/${targetLang}`)
    window.location.href = newPath
  }

  return (
    <button
      className="cursor-pointer font-semibold hover:text-blue-600"
      onClick={handleLanguageToggle}
      aria-label="Toggle Language"
      title="Toggle Language"
    >
      MN/EN
    </button>
  )
}
