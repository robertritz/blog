import rss from "@astrojs/rss"
import { getCollection } from "astro:content"
import { siteConfig } from "../../config"
import type { APIContext } from "astro"
import { isValidLanguage } from "../../i18n/config"

export async function getStaticPaths() {
  return [
    { params: { lang: "en" } },
    { params: { lang: "mn" } },
  ]
}

export async function GET(context: APIContext) {
  const { lang } = context.params
  const currentLang = lang && isValidLanguage(lang) ? lang : "en"

  const posts = (await getCollection("posts"))
    .filter((post) => post.data.lang === currentLang)
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())

  return rss({
    title: siteConfig.siteName,
    description:
      currentLang === "en"
        ? "Data scientist, sociologist, and business builder based in Mongolia"
        : "Монгол улсад төвтэй өгөгдлийн шинжлэх ухаанч, социологич, бизнес эрхлэгч",
    site: context.site || siteConfig.meta.url,
    items: posts.map((post) => {
      const slug = post.slug.replace(/^(en|mn)\//, "")
      return {
        title: post.data.title,
        pubDate: post.data.pubDate,
        description: post.data.description,
        link: `/${currentLang}/posts/${slug}/`,
      }
    }),
  })
}
