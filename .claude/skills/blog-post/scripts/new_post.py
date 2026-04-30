#!/usr/bin/env python3
"""Scaffold a new blog post for robertritz.com.

    python new_post.py --slug usd-mnt-2026-q2 \\
        --title "The tugrik weakened again. Here's where it might be heading." \\
        --claim "USD/MNT crossed 3500 in Q2 2026 — is this a new floor?" \\
        --research

Creates:
- ``src/content/posts/<slug>.mdx`` with prefilled Astro frontmatter (draft: true)
- ``public/images/<slug>/`` (empty, ready for hero + chart PNGs)
- ``research/<slug>/data/`` (only with --research)

Refuses to clobber an existing slug. The title is required so you commit
to a headline before scaffolding. The claim is optional but recommended —
it populates the description field and a body comment block.

Pass ``--follow-up <old-slug>`` to scaffold the "X years later" structure
described in references/follow-up-posts.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{0,80}$")


def project_root() -> Path:
    """Find the blog repo root by walking up from this script."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "CLAUDE.md").exists() and (parent / "src" / "content" / "posts").exists():
            return parent
    raise SystemExit("Could not locate blog repo root (looking for CLAUDE.md + src/content/posts).")


def is_valid_slug(s: str) -> bool:
    return bool(SLUG_RE.match(s))


def read_old_frontmatter(post_path: Path) -> dict:
    """Pull title and tags from an existing post's YAML frontmatter."""
    if not post_path.exists():
        return {}
    text = post_path.read_text()
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm = text[3:end].strip()
    out: dict = {}
    for line in fm.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Scaffold a new blog post.")
    p.add_argument("--slug", required=True, help="Post slug (lowercase, hyphens, 1-81 chars). Becomes the URL: /posts/<slug>/.")
    p.add_argument("--title", required=True, help="Post title (the headline).")
    p.add_argument("--claim", default="", help="One-sentence claim being tested. Becomes description + body comment.")
    p.add_argument(
        "--follow-up",
        dest="follow_up",
        metavar="OLD_SLUG",
        help="Scaffold this as a follow-up to an existing post. See references/follow-up-posts.md.",
    )
    p.add_argument(
        "--research",
        action="store_true",
        help="Also create research/<slug>/data/ for raw data and analysis scripts.",
    )
    p.add_argument(
        "--no-draft",
        action="store_true",
        help="Skip the default `draft: true` frontmatter line. Use only when you mean to publish on commit.",
    )
    args = p.parse_args()

    if not is_valid_slug(args.slug):
        raise SystemExit(
            f"Invalid slug {args.slug!r}. Use lowercase letters, digits, and hyphens; "
            f"start with alphanumeric; 1-81 chars."
        )

    root = project_root()
    post_path = root / "src" / "content" / "posts" / f"{args.slug}.mdx"
    md_post_path = root / "src" / "content" / "posts" / f"{args.slug}.md"
    image_dir = root / "public" / "images" / args.slug
    research_dir = root / "research" / args.slug

    # Refuse to clobber.
    if post_path.exists() or md_post_path.exists():
        raise SystemExit(f"Post already exists: {post_path if post_path.exists() else md_post_path}")
    if image_dir.exists() and any(image_dir.iterdir()):
        raise SystemExit(f"Image directory already exists and is non-empty: {image_dir}")

    follow_up_meta = {}
    follow_up_link = ""
    if args.follow_up:
        old_md = root / "src" / "content" / "posts" / f"{args.follow_up}.md"
        old_mdx = root / "src" / "content" / "posts" / f"{args.follow_up}.mdx"
        old = old_mdx if old_mdx.exists() else old_md
        if not old.exists():
            raise SystemExit(f"Follow-up source post not found: {args.follow_up}")
        follow_up_meta = read_old_frontmatter(old)
        follow_up_link = f"/posts/{args.follow_up}/"

    today = date.today().isoformat()

    # ---------- Build frontmatter ----------
    tags: list[str] = []
    if args.follow_up and follow_up_meta.get("tags"):
        # tags come back as a string like "[\"a\", \"b\"]" — keep as-is, append follow-up
        tag_str = follow_up_meta["tags"]
        # Best-effort: don't parse, just leave the placeholder.
        tags = [tag_str]

    frontmatter_lines = [
        "---",
        f'title: "{args.title}"',
        f'description: "{args.claim}"',
        f"pubDate: {today}",
        f'heroImage: "/images/{args.slug}/cover.png"',
        'tags: []',
        'author: "Robert Ritz"',
    ]
    if not args.no_draft:
        frontmatter_lines.append("draft: true")
    frontmatter_lines.append("---")
    frontmatter = "\n".join(frontmatter_lines)

    # ---------- Build body ----------
    if args.follow_up:
        body = _follow_up_body(args.claim, follow_up_link, args.follow_up, follow_up_meta.get("title", ""))
    else:
        body = _standard_body(args.claim)

    post_path.parent.mkdir(parents=True, exist_ok=True)
    post_path.write_text(frontmatter + "\n\n" + body + "\n")

    image_dir.mkdir(parents=True, exist_ok=True)
    (image_dir / ".gitkeep").touch()

    if args.research:
        (research_dir / "data").mkdir(parents=True, exist_ok=True)
        (research_dir / "data" / ".gitkeep").touch()
        if args.follow_up:
            prior_note = research_dir / "prior-post.md"
            prior_note.write_text(
                f"# Prior post\n\nThis post is a follow-up to: "
                f"[{follow_up_meta.get('title', args.follow_up)}]({follow_up_link})\n\n"
                f"Source file: `src/content/posts/{args.follow_up}.md`\n"
            )

    # ---------- Tell the user what just happened ----------
    print(f"Created post:    {post_path.relative_to(root)}", file=sys.stderr)
    print(f"Created images:  {image_dir.relative_to(root)}/", file=sys.stderr)
    if args.research:
        print(f"Created research: {research_dir.relative_to(root)}/", file=sys.stderr)
    print(file=sys.stderr)
    print("Next steps:", file=sys.stderr)
    print("  1. Pull data into the appropriate location (see references/data-sources.md).", file=sys.stderr)
    print(f"  2. Make charts with blog-charts. Slug them as <{args.slug}--chart-name>.", file=sys.stderr)
    print(f"  3. Drop a hero image at public/images/{args.slug}/cover.png.", file=sys.stderr)
    print("  4. Draft prose with the roberts-voice skill.", file=sys.stderr)
    print(f"  5. Preview locally: npm run dev → http://localhost:4321/posts/{args.slug}/", file=sys.stderr)
    if not args.no_draft:
        print("  6. Remove `draft: true` from the frontmatter when ready to publish.", file=sys.stderr)
    print(file=sys.stderr)
    print(str(post_path))
    return 0


def _standard_body(claim: str) -> str:
    claim_block = f"    {claim}" if claim else "    <state the question or assertion here>"
    return f"""{{/* CLAIM BEING TESTED:
{claim_block}
*/}}

{{/* HOOK — open with a personal observation, news item, or specific
   prompt (a tweet, a conversation) that motivates this claim. Don't
   start with a thesis statement. */}}

{{/* DATA — name the source with a hyperlink in the same paragraph
   you introduce it. See references/data-sources.md for what's where. */}}

{{/* ANALYSIS — chart-by-chart with brief commentary. Each chart should
   answer one small question. Use the blog-charts skill, slugged as
   <post-slug>--<chart-name>. Aim for 3-7 charts. */}}

{{/* CLOSE — what does this mean? What's still uncertain? Often best
   to end with a deeper question rather than a verdict. */}}
"""


def _follow_up_body(claim: str, original_link: str, original_slug: str, original_title: str) -> str:
    title_phrase = f'"{original_title}"' if original_title else f"the original post"
    claim_block = f"    {claim}" if claim else "    <state what we're checking against the original>"
    return f"""{{/* CLAIM / QUESTION REVISITED:
{claim_block}
*/}}

In <YEAR> I wrote about [{original_title or original_slug}]({original_link}), arguing <ORIGINAL CLAIM>. Some time has passed. Let's see what held up.

{{/* WHAT'S CHANGED — name the events / shifts since the original
   that motivate revisiting. Pandemic, dzud, election, sanctions, etc. */}}

{{/* RE-RUN — walk through the same analysis with fresh data. Reuse
   chart types where possible (visual continuity matters). Each section
   should mirror a section from the original. */}}

### What I got right and what I got wrong

{{/* Be specific. Bullet points are fine. Don't hedge.

   Right: <list specific predictions or claims that held>
   Wrong (or different now): <list what didn't hold and why> */}}

{{/* NEXT — what new questions does this raise? Sometimes set up the
   *next* revisit explicitly. */}}
"""


if __name__ == "__main__":
    raise SystemExit(main())
