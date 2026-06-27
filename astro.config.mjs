import { defineConfig } from "astro/config"

import react from "@astrojs/react"
import sitemap from "@astrojs/sitemap"
import mdx from "@astrojs/mdx"
import pagefind from "astro-pagefind"
import robotsTxt from "astro-robots-txt"
import tailwindcss from "@tailwindcss/vite"

// https://astro.build/config
export default defineConfig({
  output: "static",
  prefetch: true,
  site: "https://robertritz.com",
  integrations: [react(), sitemap(), mdx(), pagefind(), robotsTxt()],
  markdown: {
    shikiConfig: {
      theme: "css-variables",
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
})
