import { defineCollection, z } from "astro:content"

const postSchema = z.object({
  title: z.string(),
  description: z.string(),
  pubDate: z.coerce.date(),
  updatedDate: z.coerce.date().optional(),
  heroImage: z.string().optional(),
  ogImage: z.string().optional(),
  tags: z.array(z.string()).optional(),
  translationId: z.string().optional(),
})

const pageSchema = z.object({
  title: z.string(),
  description: z.string(),
  updatedDate: z.coerce.date().optional(),
  heroImage: z.string().optional(),
  ogImage: z.string().optional(),
})

const postsCollection = defineCollection({
  type: "content",
  schema: postSchema,
})

const blogCollection = defineCollection({
  type: "content",
  schema: postSchema,
})

const aboutCollection = defineCollection({
  type: "content",
  schema: pageSchema, // Using the simpler page schema for about pages
})

export const collections = {
  posts: postsCollection,
  blog: blogCollection,
  about: aboutCollection,
}
