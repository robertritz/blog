# Project Setup: Astro Blog with astro-air Theme

## Task List

- [x] Initialize Astro project with astro-air theme
- [x] Configure for English (default) and Mongolian support
  - [x] Updated language toggle component
  - [x] Updated content configuration
  - [x] Created Mongolian posts directory
  - [x] Updated README.md
  - [x] Removed Chinese language directory
  - [x] Updated all remaining zh references to mn:
    - [x] header.astro
    - [x] nav.astro (removed)
    - [x] twikoo.astro (updated language setting)
    - [x] base.astro
    - [x] rss.xml.ts (both in pages/ and pages/[lang]/)
    - [x] utils/index.ts (updated collection name)
- [x] Remove GitHub link from header (`src/components/astro/header.astro`)
- [x] Change language icon to text MN/EN (`src/components/react/language-toggle.tsx`)
- [x] Remove Links menu item (`src/components/astro/nav.astro`)
- [x] Remove Links page (`src/pages/[lang]/links/index.astro`)
- [x] Update footer text (`src/components/astro/footer.astro`)
- [x] Move RSS feed link from header to footer (`src/components/astro/header.astro`, `src/components/astro/footer.astro`)
- [x] Remove About pages (`src/config/en/about.mdx`, `src/config/mn/about.mdx`)
- [x] Remove About link from navigation (`src/components/astro/nav.astro`)
- [x] Make site title link language-specific (`src/components/astro/header.astro`)
- [x] Move Archive link to header, next to language toggle (`src/components/astro/header.astro`)
- [x] Remove Nav component (`src/components/astro/nav.astro`)
- [x] Remove Nav component import/usage from `main.astro` layout
- [x] Delete sample blog posts (`src/content/blog/en/hello-world.mdx`, `src/content/blog/mn/hello-world.mdx`)
- [x] Delete old blog posts from `src/content/posts/` directory
- [x] Add new blog post "8090 isn't the future" in English (`src/content/blog/en/8090-isnt-the-future.md`)
- [x] Add Mongolian translation for the new blog post (`src/content/blog/mn/8090-ирээдүй-биш.md`)
- [x] Fix frontmatter schema errors in new blog posts (add `description`, rename `date` to `pubDate`)
- [ ] Customize site configuration (Review remaining items)
- [ ] Test the blog locally
- [ ] Deploy the blog (if needed)

## Current Step

- Fixed content collection schema errors in the new English and Mongolian blog posts by adding the `description` field and renaming `date` to `pubDate`.

Previously:

- Deleted all sample/old blog posts from `src/content/blog/` and `src/content/posts/` directories.
- Added a new blog post titled "8090 isn't the future" in English to `src/content/blog/en/`.
- Added the Mongolian translation of the post to `src/content/blog/mn/`.
- Both posts share the same `translationId` for linking.

Simplified header:

- Site title now links to the language-specific home page.
- Added Archive link next to the language toggle.
- Removed the separate navigation bar component (`nav.astro`).

Configured site settings in `src/config/index.ts`:

- Set domain, URL, site names, titles, descriptions.
- Updated social links (GitHub, X).
- Disabled Links navigation.
- Disabled comments.

Basic setup is complete. You still need to:

1. Create intro descriptions for both languages:
   - `/src/config/en/intro.mdx`
   - `/src/config/mn/intro.mdx`

## Deployment Setup

- [x] Created Dockerfile for Astro blog deployment
  - Using node:20-alpine for build
  - Using nginx:alpine for serving static files
  - Added healthcheck configuration
- [x] Updated deploy.yml for Kamal deployment
  - Added healthcheck configuration with path, port, interval, timeout, and max_attempts
  - Kept existing SSL and proxy configuration

The deployment setup uses a two-stage build process:
1. Build stage: Uses Node.js to build the Astro static site
2. Production stage: Uses Nginx to serve the static files

Astro is configured with `output: "static"` in astro.config.mjs, which means it generates static HTML files that can be served by any web server like Nginx.

## Next Steps

1. Review remaining customization tasks in `src/config/`.
2. Run `bun run dev` (or `npm run dev`) to start the development server for local testing.
3. Deploy the blog using Kamal:
   ```
   kamal setup
   kamal deploy
   ```
