import { defineCollection, z } from "astro:content"

const postSchema = z.object({
  title: z.string(),
  description: z.string(),
  pubDate: z.coerce.date(),
  updatedDate: z.coerce.date().optional(),
  heroImage: z.string().optional(),
  ogImage: z.string().optional(),
  tags: z.array(z.string()).optional(),
  lang: z.enum(["en", "mn"]).default("en"),
  author: z.string().optional(),
  excerpt: z.string().optional(),
  translationId: z.string().optional(),
})

const postsCollection = defineCollection({
  type: "content",
  schema: postSchema,
})

export const collections = {
  posts: postsCollection,
}
