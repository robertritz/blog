# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Git Workflow (IMPORTANT)

**Before starting work:**

```bash
git fetch origin
git status  # Check if behind remote
git pull    # Pull any changes from other machine
```

**When work is complete:**

```bash
git add -A
git commit -m "Description of changes"
git push
```

Robert syncs work between two machines via GitHub. Always check for remote changes before starting.

## Overview

Robert Ritz's personal blog (robertritz.com) - a minimalist static site built with Astro and deployed via Kamal. Inspired by world.hey.com with a clean, text-focused design.

## Technology Stack

- **Framework**: Astro (static site generator)
- **Styling**: Tailwind CSS with custom styles
- **Deployment**: Kamal (Docker-based)
- **Server**: Nginx (serving static files)

## URL Structure

Simple, clean URLs without language prefixes:

```
/                    → Homepage
/posts/post-slug/    → Individual post
/archive/            → All posts
/rss.xml             → RSS feed
```

## Content Structure

Posts are stored directly in `src/content/posts/`:

```
src/content/posts/
├── my-first-post.md
├── another-post.md
└── ...
```

**Post Frontmatter Schema** (`src/content.config.ts`):

```typescript
{
  title: string              // Post title
  description: string        // Short description/excerpt
  pubDate: Date             // Publication date
  updatedDate?: Date        // Optional update date
  heroImage?: string        // Optional hero image
  ogImage?: string          // Optional Open Graph image
  tags?: string[]           // Optional tags
  author?: string           // Optional author name
  excerpt?: string          // Optional excerpt
}
```

## Adding New Content

Create a new markdown file in `src/content/posts/`:

```markdown
---
title: "My New Post"
description: "A brief description"
pubDate: 2025-01-15
author: "Robert Ritz"
---

Your content here...
```

## Development Workflow

### Local Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
# Visit http://localhost:4321/

# Build for production
npm run build

# Preview production build
npm run preview
```

### Code Quality

Pre-commit hooks (via lefthook):

- **eslint** - Lints TypeScript/JavaScript files
- **prettier** - Formats all files

## Deployment

### With Kamal

The blog is deployed to a Hetzner server (78.46.40.253) using Kamal:

```bash
# Deploy to production
cd /path/to/blog
kamal deploy
```

**Important**: Kamal builds from the git repository, so:

1. **Commit your changes first** before deploying
2. Uncommitted changes will NOT be deployed

**Deployment Configuration** (`config/deploy.yml`):

- Service name: `blog`
- Docker image: `robertritz/blog`
- Server: 78.46.40.253
- Domain: robertritz.com
- SSL: Enabled (Let's Encrypt via kamal-proxy)
- Builder: Docker Build Cloud (amd64 architecture)

## Project Structure

```
blog/
├── src/
│   ├── components/          # Reusable components
│   │   ├── BaseHead.astro   # SEO & meta tags
│   │   ├── Bio.astro        # Author bio
│   │   ├── FormattedDate.astro  # Date formatting
│   │   ├── Header.astro
│   │   ├── Footer.astro
│   │   └── SystemTheme.astro    # Dark/light mode
│   ├── content/
│   │   └── posts/           # Blog posts (markdown)
│   ├── pages/
│   │   ├── index.astro      # Homepage
│   │   ├── archive.astro    # Archive page
│   │   ├── 404.astro        # Error page
│   │   ├── rss.xml.ts       # RSS feed
│   │   └── posts/
│   │       └── [...slug].astro  # Post pages
│   ├── config/
│   │   └── index.ts         # Site configuration
│   ├── styles/              # Global styles
│   └── types/               # TypeScript types
├── research/                # In-progress research (not necessarily posts)
├── public/
│   ├── avatar.png           # Profile picture (used as favicon too)
│   ├── fonts/               # Custom fonts
│   └── images/              # Post images (organized by post slug)
├── config/
│   └── deploy.yml           # Kamal deployment config
├── Dockerfile               # Multi-stage Docker build
├── astro.config.mjs         # Astro configuration
├── tailwind.config.mjs      # Tailwind configuration
├── package.json
└── CLAUDE.md                # This file
```

## Images

Images live in `public/images/` organized by post slug:

```
public/images/
├── fuel-shortage/          # Images for mongolia-is-running-on-fumes post
├── meat_prices/            # Images for mongolian-meat-price-time-series-forecast post
├── market_prices/          # Images for which-grocery-store post
└── ...
```

**Convention**: Each post gets its own subdirectory under `public/images/`. Reference images using absolute paths from the public root:

- **Hero image** (frontmatter): `heroImage: "/images/post-slug/cover.jpg"`
- **Inline image** (markdown): `![](/images/post-slug/filename.png)`

## Research Directory

The `research/` directory contains in-progress research projects that may or may not become blog posts. These are exploratory analyses, data investigations, and working notebooks.

Current projects: `consumer-confidence-mongolia`, `mongolia-data-governance`, `sentencing-bias`, `usd-mnt-forecast`

## Skills

- **`blog-post`** — Use this skill when starting a new post. Scaffolds `src/content/posts/<slug>.mdx` with prefilled frontmatter (`draft: true`), `public/images/<slug>/`, and optionally `research/<slug>/`. Encodes the 5-part post pattern (hook → claim → data → analysis → close), the data sources Robert uses (NSO 1212.mn, Mongolbank, MRPAM, World Bank, data.mn), and the "X years later" follow-up structure. Composes with `roberts-voice` and `blog-charts`.
- **`roberts-voice`** — Use this skill when writing or drafting blog posts. It captures Robert's writing voice and style for data stories, articles, and written content.
- **`blog-charts`** — Use this skill when creating any chart or data visualization for new blog posts. Wraps the Datawrapper API: creates, styles, publishes, and PNG-exports charts from a CSV. Default output is a responsive interactive iframe for `.mdx` posts; PNG fallback works in `.md`. Slug registry at `~/.cache/blog-charts/registry.json` prevents duplicates. Read `references/principles.md` (SWD + Economist data team) before drafting any chart's title.
- **`chart-maker`** (deprecated) — Old matplotlib-based skill. Kept only so old posts that reference its templates still build. **Do not use for new charts** — use `blog-charts` instead.

## Secrets

`/Users/ritz/projects/blog/.env` (gitignored) carries:

| Var | Used by | Notes |
|---|---|---|
| `DATAWRAPPER_API_TOKEN` | `blog-charts` skill | Free-tier Datawrapper. See `.claude/skills/blog-charts/references/secrets.md` for required scopes and smoke-test. |

## Charts and MDX

The `blog-charts` skill emits a responsive iframe with an inline resize
script. Astro's plain markdown integration may strip script tags — for
posts that include interactive Datawrapper embeds, save the post as
`.mdx` (Astro's MDX integration is loaded in `astro.config.mjs`). Plain
`.md` posts can fall back to a PNG export — see
`.claude/skills/blog-charts/references/embeds.md`.

## Design Philosophy

- **Minimalist**: Inspired by world.hey.com - simple, clean, readable
- **No JavaScript dependencies** for core functionality (only for theme toggle)
- **Static generation**: All pages pre-built for maximum performance
- **SEO-friendly**: Proper meta tags, sitemap, RSS feed

## Important Notes

1. **Git Workflow**: Always commit before deploying with Kamal (builds from git, not working directory)

2. **TypeScript**: The Dockerfile bypasses type checking during deployment. Fix errors locally with `npm run build`.

## Troubleshooting

**Build fails with TypeScript errors:**

- The Dockerfile bypasses type checking during deployment
- Fix locally with `npm run build` to see errors

**Kamal deployment deploys old code:**

- Kamal builds from git repository
- Run `git status` to check for uncommitted changes
- Commit changes before `kamal deploy`
