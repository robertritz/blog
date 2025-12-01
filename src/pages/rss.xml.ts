import rss from "@astrojs/rss"
import { getCollection } from "astro:content"
import { siteConfig } from "../config"

export async function GET(context: any) {
  const posts = (await getCollection("posts"))
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())

  return rss({
    title: siteConfig.siteName,
    description: siteConfig.meta.description,
    site: context.site || siteConfig.meta.url,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.pubDate,
      description: post.data.description,
      link: `/posts/${post.slug}/`,
    })),
  })
}
