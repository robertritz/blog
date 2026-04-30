---
name: blog-post
description: >
  Scaffold and structure new blog posts for robertritz.com. The
  `new_post.py` script creates `src/content/posts/<slug>.mdx` with
  prefilled Astro frontmatter (`draft: true` by default),
  `public/images/<slug>/` for the hero and inline charts, and optionally
  `research/<slug>/` for raw data. The `migrate_post.py` script renames
  legacy image folders on old posts to match their slug (use lazily, only
  when editing an old post for another reason — see CLAUDE.md). Encodes
  the 5-part post pattern (hook → claim → data → analysis → close), the
  data sources Robert uses (NSO 1212.mn, Mongolbank, MRPAM, World Bank,
  data.mn), and the distinctive "X years later" follow-up structure
  (`--follow-up <old-slug>` flag). Composes with `roberts-voice` (prose)
  and `blog-charts` (Datawrapper). Does NOT generate prose or build
  charts — those belong to the companion skills. Triggers on: new post,
  blog post, draft post, write a post, scaffold post, start a post,
  publish a post, claim test, data story, follow-up post, X years later,
  blog-post, new_post, migrate post, rename image folder, fix legacy
  image folder, migrate_post.
---

# Blog Post

Tools and conventions for starting a new blog post on robertritz.com.
Intentionally simple — this is scaffolding plus a few reference docs that
capture Robert's existing pattern. Not a research framework. Compose with
`roberts-voice` for prose and `blog-charts` for charts.

## When to Use

| Situation | Action |
|---|---|
| Starting a new post | `new_post.py --slug <slug> --title "..."` |
| Starting a follow-up to an old post ("X years later") | `new_post.py --slug <slug> --title "..." --follow-up <old-slug>` |
| Need data + scripts alongside the post | `new_post.py ... --research` |
| Existing post has a legacy image folder name that doesn't match its slug | `migrate_post.py --post <slug>` (dry-run by default) |
| Drafting prose | invoke `roberts-voice` |
| Adding a chart | invoke `blog-charts` |

## The Standard Flow

```bash
# 1. Scaffold. Creates the .mdx file (with draft: true), the image folder,
#    and a research/ folder if you pass --research.
python .claude/skills/blog-post/scripts/new_post.py \
    --slug usd-mnt-2026-q2 \
    --title "The tugrik weakened again. Here's where it might be heading." \
    --claim "USD/MNT crossed 3500 in Q2 2026 — is this a new floor or a temporary peak?" \
    --research

# 2. Pull data into research/usd-mnt-2026-q2/data/ from your sources
#    (NSO 1212.mn, Mongolbank, etc. — see references/data-sources.md).

# 3. Make charts. Each chart's slug is namespaced by the post slug.
python .claude/skills/blog-charts/scripts/dw_create.py \
    --slug usd-mnt-2026-q2--exchange-rate \
    --type d3-lines --csv ./research/usd-mnt-2026-q2/data/usd-mnt.csv \
    --title "..." --intro "..." \
    --source-name "Mongolbank"

# 4. Draft prose. Invoke `roberts-voice`. Reference the post-structure
#    template in references/post-structure.md.

# 5. Local preview. The post is currently draft: true and won't appear
#    publicly until you remove that line.
npm run dev
# visit http://localhost:4321/posts/usd-mnt-2026-q2/

# 6. Publish. Remove `draft: true` from the frontmatter, commit, push.
git add src/content/posts/usd-mnt-2026-q2.mdx public/images/usd-mnt-2026-q2/
git commit -m "Publish: <title>"
git push
```

## Routing — Read the Right Reference

Progressive disclosure. Don't load everything.

| Need | Reference | When to read |
|---|---|---|
| The 5-part post pattern with annotated examples | `references/post-structure.md` | Always read **before drafting**. The shape of a post matters. |
| Where to find Mongolian and international data | `references/data-sources.md` | When you need a number and don't know which source has it |
| The "X years later" follow-up pattern | `references/follow-up-posts.md` | Only when revisiting an old post |

## What This Skill Doesn't Do

- **Doesn't write prose.** That's `roberts-voice` plus you. The scaffold's body is just a structural outline (as MDX comments) you fill in.
- **Doesn't make charts.** That's `blog-charts`. Use the slug convention `<post-slug>--<chart-name>` so charts trace to their post.
- **Isn't a research framework.** No claim decomposition, scenario matrices, or simulation modeling. If you want that, see `~/projects/american_metrics/.claude/skills/american-metrics-research`. Most of Robert's posts don't need it.
- **Doesn't fetch data.** Pulling CSVs from NSO/Mongolbank/etc. is manual or notebook-driven work. The data-sources reference tells you where to look; the actual fetch is up to you.

## File Layout for a New Post

After running `new_post.py --slug X --research`:

```
src/content/posts/X.mdx              ← Frontmatter prefilled, body is a 5-part outline
public/images/X/                     ← Empty. Drop hero (cover.png) and chart PNGs here.
research/X/                          ← Only created with --research.
└── data/                            ← CSVs, raw downloads.
```

Image folder name and post slug **always match** for new posts. (Old
posts have legacy folder names that don't — see `migrate_post.py` if you
want to fix one.)

## Drafts

Posts default to `draft: true` in the frontmatter. Astro filters drafts
out of the homepage, archive, RSS, and route generation, so a half-
written post can't accidentally publish. Remove the line (or set it to
`false`) when you're ready to ship.

There is no separate `drafts/` directory. Everything lives in
`src/content/posts/`. Use `git status` to see what's in flight.

## Companion Skills

- **`roberts-voice`** — for prose. Invoke when drafting body text.
- **`blog-charts`** — for charts. Slug your charts as `<post-slug>--<chart-name>`.
- **`chart-maker`** (deprecated) — kept for backward compat with old posts.
