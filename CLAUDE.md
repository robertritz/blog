# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

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
├── public/
│   ├── avatar.png           # Profile picture (used as favicon too)
│   └── fonts/               # Custom fonts
├── config/
│   └── deploy.yml           # Kamal deployment config
├── Dockerfile               # Multi-stage Docker build
├── astro.config.mjs         # Astro configuration
├── tailwind.config.mjs      # Tailwind configuration
├── package.json
└── CLAUDE.md                # This file
```

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
