# Robert Ritz Blog

A minimalist blog inspired by world.hey.com, built with Astro.

## 🚀 Quick Start

```bash
npm install
npm run dev
```

Visit `http://localhost:4321` to see your blog.

## 📝 Adding New Posts

1. Create a new `.md` file in `src/content/posts/en/`
2. Use this frontmatter template:

```markdown
---
title: "Your Post Title"
author: "Robert Ritz"
pubDate: "2025-01-15"
description: "Brief description of your post"
lang: "en"
---

Your content here...
```

3. The post will automatically appear on your homepage and archive page.

## ✏️ Updating Your Bio

Your bio appears in two places but is managed in one file:

**Edit your bio in:** `src/components/Bio.astro`

This component is automatically used on:
- Homepage (under your name)
- Post pages (in the "About Robert Ritz" section at the bottom)

Update it once, and both places will reflect the changes!

## 🎨 Customization

### Profile Picture
- Replace `/public/avatar.png` with your photo
- It's used as the favicon and profile image throughout the site

### Site Configuration
Edit `src/config/index.ts` to update:
- Site name and description
- Social media links
- Domain URL

### Styling
- Main styles are in each `.astro` file's `<style>` section
- Global styles are in `src/styles/global.css`

## 📦 Deployment

### Build for Production
```bash
npm run build
```

### Deploy with Kamal
Your existing Kamal setup should work:
```bash
kamal setup    # First time only
kamal deploy   # Deploy updates
```

## 🔧 Development Commands

```bash
npm run dev        # Start dev server
npm run build      # Build for production  
npm run preview    # Preview production build
npm run format     # Format code with Prettier
```

## 📁 Key Files & Directories

```
src/
├── components/         # Reusable components
├── content/posts/en/   # Your blog posts (add new posts here)
├── pages/
│   ├── index.astro     # Homepage (edit bio here)
│   ├── posts/[...slug].astro  # Post pages (edit about section here)
│   └── archive.astro   # All posts page
├── config/index.ts     # Site configuration
└── styles/             # Global styles

public/
├── avatar.png          # Your profile picture (replace this)
└── ...                 # Static assets
```

## 🌟 Features

- ✅ Minimalist design inspired by world.hey.com
- ✅ Automatic dark/light mode based on system preference
- ✅ RSS feed
- ✅ Mobile responsive
- ✅ Fast static site generation
- ✅ SEO optimized

## 📖 Writing Tips

- Keep post filenames descriptive (e.g., `my-thoughts-on-ai.md`)
- Use the `description` field for post previews on homepage
- Posts are sorted by `pubDate` (newest first)
- Markdown syntax is fully supported

Happy blogging! 🎉
