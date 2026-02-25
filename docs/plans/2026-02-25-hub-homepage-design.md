# Hub Homepage Redesign

## Goal

Transform robertritz.com from a Dario Amodei-style minimal blog clone into a builder/maker hub that connects three properties: the blog, Mongolia Newsletter (mongolia.robertritz.com), and Data.mn.

## Tone

Builder / maker. The homepage says: here's who I am, here's what I'm building, here's what I'm writing.

## Page Structure (top to bottom)

### Header

- Left: "Robert Ritz" in Georgia serif, bold, linked to `/`
- Right: "Writing" and "Projects" as text links (Inter, small, gray) + dark mode toggle
- Consistent across homepage, archive, and post pages
- Mobile: name left, toggle right; nav links below or omitted (homepage is the nav)

### Bio

2-3 sentences, no expand/collapse:

> Data scientist, builder, and accidental Mongolian. I moved to Ulaanbaatar over a decade ago and now run a university, co-founded a furniture company, and build tools to make Mongolia's data accessible.

### Projects (featured pair + roles line)

Mongolia Newsletter leads (direct audience). Data.mn follows (credibility anchor).

```
Projects

Mongolia Newsletter
Weekly digest of Mongolian news, politics, and economics.
mongolia.robertritz.com →

Data.mn
Making Mongolia's data accessible and searchable.
data.mn →

Also: President of AUM · Co-founder, Precision Kraft
```

- Featured projects: name in bold, one-line description in secondary gray, URL as link with arrow
- Project links get a subtle permanent underline or distinct treatment so they register as interactive without a bright accent color
- "Also:" line is a single editable line (AUM may be removed later)

### Writing

Latest 5 posts as bulleted links with date in gray. "See all →" links to /archive.

```
Writing

• A world where AI has all the answers    Dec 2025

See all →
```

### Footer

```
X · Email · RSS
```

One line, small, gray. Centered or left-aligned.

## Visual System

| Property | Value |
|----------|-------|
| Background (light) | `#fafafa` |
| Background (dark) | `#1a1a1a` |
| Body font | Inter |
| Name font | Georgia serif (for "Robert Ritz" only) |
| Section headings | Inter bold |
| Text color (light) | `#1f1e1d` |
| Text color (dark) | `#e5e5e5` |
| Secondary text | `#6b7280` (descriptions, dates, "Also:" line) |
| Link color | `#1f1e1d` / `#e5e5e5` with underline on hover |
| Project link treatment | Subtle permanent underline or distinct weight |
| Max-width | 640px, centered |
| Section spacing | ~48px between sections |
| Line height | 1.7 (body), 1.2 (headings) |

Design principle: hierarchy through typography, spacing, and weight. No cards, borders, or decoration.

## SEO / Meta

Update OG description to: "Builder based in Mongolia. Making data accessible, writing about AI and economics, running AUM and Precision Kraft."

## What We Deliberately Did Not Add

- No About page (bio handles it; easy to add later)
- No newsletter subscribe form (link to subdomain is cleaner)
- No avatar/images (text-forward, fast)
- No bright accent colors (dark text links with underline treatment)

## Technical Notes

- Framework: Astro (static site generator)
- Modify: `src/pages/index.astro` (homepage), update styles
- Add Inter font (Google Fonts or self-hosted woff2)
- Header component should be extracted for reuse across homepage, archive, and post pages
- Update `src/config/index.ts` meta description
- Update `src/components/BaseHead.astro` if needed for OG tags
