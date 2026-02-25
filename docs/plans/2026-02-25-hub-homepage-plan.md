# Hub Homepage Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign robertritz.com homepage as a builder/maker hub connecting the blog, Mongolia Newsletter, and Data.mn.

**Architecture:** Replace the current single-section homepage with a multi-section hub (header, bio, projects, writing, footer). Extract a shared header component used across all pages. Switch from Atkinson/system fonts to Inter (body) + Georgia (name only). Update background from beige to clean white.

**Tech Stack:** Astro 5, scoped CSS (no Tailwind for page styles), self-hosted Inter font

---

### Task 1: Add Inter font files

**Files:**
- Create: `public/fonts/inter-regular.woff2`
- Create: `public/fonts/inter-bold.woff2`
- Modify: `src/components/BaseHead.astro:32-46`

**Step 1: Download Inter woff2 files**

Run:
```bash
cd /home/ritz/projects/blog
curl -L "https://fonts.gstatic.com/s/inter/v18/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuLyfMZhrib2Bg-4.woff2" -o public/fonts/inter-regular.woff2
curl -L "https://fonts.gstatic.com/s/inter/v18/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuFuYMZhrib2Bg-4.woff2" -o public/fonts/inter-bold.woff2
```

**Step 2: Update BaseHead.astro font preloads**

Replace the Atkinson preloads (lines 32-46) with Inter preloads:

```astro
<!-- Font preloads -->
<link
  rel="preload"
  href="/fonts/inter-regular.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>
<link
  rel="preload"
  href="/fonts/inter-bold.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>
```

**Step 3: Update global.css @font-face declarations**

In `src/styles/global.css`, replace the Atkinson @font-face blocks (lines 19-32) with:

```css
@font-face {
  font-family: "Inter";
  src: url("/fonts/inter-regular.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Inter";
  src: url("/fonts/inter-bold.woff2") format("woff2");
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}
```

Also update the body font-family (line 34) from `"Atkinson"` to `"Inter"`.

**Step 4: Verify dev server starts**

Run: `cd /home/ritz/projects/blog && npm run dev`
Expected: Dev server starts, no font loading errors in browser console.

**Step 5: Commit**

```bash
git add public/fonts/inter-regular.woff2 public/fonts/inter-bold.woff2 src/components/BaseHead.astro src/styles/global.css
git commit -m "feat: replace Atkinson font with Inter"
```

---

### Task 2: Create shared SiteHeader component

**Files:**
- Create: `src/components/SiteHeader.astro`

**Step 1: Create the SiteHeader component**

```astro
---
interface Props {
  showNav?: boolean
}

import SystemTheme from "./SystemTheme.astro"

const { showNav = true } = Astro.props
---

<header class="site-header">
  <a href="/" class="site-name">Robert Ritz</a>
  <div class="header-right">
    {showNav && (
      <nav class="site-nav">
        <a href="/#projects" class="nav-link">Projects</a>
        <a href="/#writing" class="nav-link">Writing</a>
      </nav>
    )}
    <SystemTheme />
  </div>
</header>

<style>
  .site-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 48px;
  }

  .site-name {
    font-family: Georgia, "Times New Roman", Times, serif;
    font-size: 20px;
    font-weight: 700;
    color: #1f1e1d;
    text-decoration: none;
  }

  [data-theme="dark"] .site-name {
    color: #e5e5e5;
  }

  .site-name:hover {
    opacity: 0.7;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 24px;
  }

  .site-nav {
    display: flex;
    gap: 20px;
  }

  .nav-link {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
    color: #6b7280;
    text-decoration: none;
  }

  .nav-link:hover {
    color: #1f1e1d;
  }

  [data-theme="dark"] .nav-link:hover {
    color: #e5e5e5;
  }

  @media (max-width: 600px) {
    .site-nav {
      display: none;
    }
  }
</style>
```

**Step 2: Verify it renders**

Import and use it temporarily in `index.astro` to verify. Check the dev server.

**Step 3: Commit**

```bash
git add src/components/SiteHeader.astro
git commit -m "feat: add shared SiteHeader component with nav links"
```

---

### Task 3: Rewrite homepage

**Files:**
- Modify: `src/pages/index.astro` (full rewrite)
- Modify: `src/config/index.ts:9`

**Step 1: Update site config meta description**

In `src/config/index.ts`, change the description (line 9) to:

```typescript
description: "Builder based in Mongolia. Making data accessible, writing about AI and economics, running AUM and Precision Kraft.",
```

**Step 2: Rewrite index.astro**

Replace the entire file with the new hub homepage. The page structure is:
1. SiteHeader (with nav hidden on homepage since the sections are visible)
2. Bio paragraph (no expand/collapse)
3. Projects section (Mongolia Newsletter, Data.mn, roles line)
4. Writing section (latest posts with dates)
5. Footer (X, Email, RSS)

Key details:
- Body font: `"Inter", -apple-system, BlinkMacSystemFont, sans-serif`
- Background: `#fafafa` (light), `#1a1a1a` (dark)
- Max-width: `640px`
- Section headings: Inter bold, 18px, uppercase letter-spacing for subtle separation
- Project names: Inter bold, 17px
- Project descriptions: 15px, `#6b7280`
- Project links: 15px, `#6b7280`, permanent underline, darken on hover
- "Also:" line: 15px, `#6b7280`, italic
- Post list: bullet list, post title as link, date right-aligned in gray
- Footer: 14px, gray, centered

The homepage should NOT show nav links in the header (the sections are already on-page). Use `<SiteHeader showNav={false} />`.

Section IDs: `id="projects"` and `id="writing"` on the section elements so nav links from other pages can deep-link.

**Step 3: Check in browser**

Run dev server, verify:
- [ ] Bio renders as plain paragraph, no expand/collapse
- [ ] Projects section shows Mongolia Newsletter first, Data.mn second
- [ ] "Also:" line shows AUM and Kraft
- [ ] Writing section shows posts with dates
- [ ] Footer shows X, Email, RSS
- [ ] Dark mode works (toggle + system preference)
- [ ] Mobile responsive (nav links hidden, spacing tightens)
- [ ] Background is clean white, not beige

**Step 4: Commit**

```bash
git add src/pages/index.astro src/config/index.ts
git commit -m "feat: redesign homepage as builder/maker hub"
```

---

### Task 4: Update archive page

**Files:**
- Modify: `src/pages/archive.astro`

**Step 1: Update archive to use SiteHeader and new visual system**

Replace the inline header with `<SiteHeader />` (with nav visible). Update:
- Background: `#fafafa` / `#1a1a1a`
- Body font: `"Inter", -apple-system, ...`
- Max-width: `640px` (was 600px)
- Section headings: Inter bold (not serif)
- Keep the existing post listing structure but match new typography

**Step 2: Verify in browser**

- [ ] Header matches homepage style with nav links visible
- [ ] "Projects" link goes to `/#projects`
- [ ] "Writing" link goes to `/#writing`
- [ ] Post listing typography matches new system

**Step 3: Commit**

```bash
git add src/pages/archive.astro
git commit -m "feat: update archive page with shared header and new visual system"
```

---

### Task 5: Update post page

**Files:**
- Modify: `src/pages/posts/[...slug].astro`

**Step 1: Update post page header and visual system**

This is the most complex page. Changes needed:
- Background: `#fafafa` / `#1a1a1a` (replace all `#f0eee6` references)
- Body font: `"Inter"` everywhere system font stack appears
- Keep serif for post title h1 (Georgia) and content h2/h3
- Fixed header: update background to `#fafafa` / `#1a1a1a`
- Replace the inline `.site-name` / `.header-center` with `<SiteHeader />` adapted for fixed positioning
- TOC sidebar background: update to `#fafafa` / `#1a1a1a`

Note: The post page has a fixed header and TOC sidebar that complicate a simple component swap. The SiteHeader may need to be inlined here or the component made flexible enough to handle fixed positioning. Preferred approach: keep SiteHeader for the markup/nav but apply post-specific positioning overrides in the page's scoped CSS using `:global(.site-header)`.

**Step 2: Verify in browser**

- [ ] Post page background is white, not beige
- [ ] Header matches other pages visually
- [ ] TOC sidebar still works (desktop + mobile drawer)
- [ ] Dark mode works throughout
- [ ] Content typography uses Inter for body, Georgia for headings

**Step 3: Commit**

```bash
git add src/pages/posts/[...slug].astro
git commit -m "feat: update post page with new visual system"
```

---

### Task 6: Clean up old font files and global.css

**Files:**
- Delete: `public/fonts/atkinson-regular.woff` (if no longer referenced)
- Delete: `public/fonts/atkinson-bold.woff` (if no longer referenced)
- Modify: `src/styles/global.css`

**Step 1: Search for any remaining Atkinson references**

Run: `grep -r "atkinson\|Atkinson" src/`

If no results, delete the old font files.

**Step 2: Update global.css body background**

The global.css still has Bear Blog's gradient background (line 38). Since each page now defines its own background in scoped styles, either:
- Update global.css body background to `#fafafa` as the default
- Or remove it entirely and let page-level styles handle it

Preferred: set global.css body to `background: #fafafa;` and `[data-theme="dark"] body { background: #1a1a1a; }` so there's a consistent base.

**Step 3: Verify build succeeds**

Run: `cd /home/ritz/projects/blog && npm run build`
Expected: Build succeeds with no errors.

**Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove Atkinson font, update global styles to new visual system"
```

---

### Task 7: Final visual QA

**No files to modify — verification only.**

Run dev server and check all pages:

**Homepage (`/`):**
- [ ] Clean white background
- [ ] "Robert Ritz" in Georgia serif, bold
- [ ] No nav links in header (homepage shows sections directly)
- [ ] Bio is 2-3 sentences, plain text, Inter font
- [ ] Projects: Mongolia Newsletter first, Data.mn second
- [ ] Project links have permanent underline, darken on hover
- [ ] "Also:" line shows AUM and Kraft
- [ ] Writing: posts with dates
- [ ] Footer: X, Email, RSS
- [ ] Dark mode: all sections readable, no beige remnants
- [ ] Mobile: nav hidden, spacing tightens, everything readable

**Archive (`/archive`):**
- [ ] Shared header with nav links
- [ ] Same white background
- [ ] Post listing readable

**Post page (`/posts/a-world-where-ai-has-all-the-answers/`):**
- [ ] White background throughout
- [ ] Header consistent
- [ ] TOC sidebar works on desktop
- [ ] TOC drawer works on mobile
- [ ] Content typography: Inter body, Georgia headings

If all checks pass, the implementation is complete.
