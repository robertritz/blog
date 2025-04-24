import { getCollection } from "astro:content"

export const formatDate = (
  date: Date | string | undefined,
  format: string = "YYYY-MM-DD",
): string => {
  const validDate = date ? new Date(date) : new Date()

  const tokens: Record<string, string> = {
    YYYY: validDate.getFullYear().toString(),
    MM: String(validDate.getMonth() + 1).padStart(2, "0"),
    DD: String(validDate.getDate()).padStart(2, "0"),
    HH: String(validDate.getHours()).padStart(2, "0"),
    mm: String(validDate.getMinutes()).padStart(2, "0"),
    ss: String(validDate.getSeconds()).padStart(2, "0"),
  }

  return format.replace(/YYYY|MM|DD|HH|mm|ss/g, (match) => tokens[match])
}

export const getPostsByLocale = async (locale: string) => {
  const allPosts = await getCollection("posts")
  const localizedPosts = allPosts.filter(post => {
    const pathParts = post.slug.split('/')
    return pathParts[0] === locale
  })
  return localizedPosts.sort(
    (a: any, b: any) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
  )
}

export const getTranslatedPost = async (currentSlug: string, targetLang: string) => {
  const allPosts = await getCollection("posts")
  const currentPost = allPosts.find(post => post.slug === currentSlug)
  
  if (!currentPost?.data.translationId) {
    return null
  }

  return allPosts.find(
    post => 
      post.slug.startsWith(targetLang) && 
      post.data.translationId === currentPost.data.translationId
  )
}
