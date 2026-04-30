#!/usr/bin/env python3
"""Rename a legacy image folder so it matches its post slug.

Background: posts predating the Astro migration use image folder names
that don't match the SEO-optimized post slug. For example, the post
``do-families-with-more-children-make-less-money`` references images
at ``/images/wages_by_children/``. This script fixes a single post:

1. Finds all ``/images/<old-folder>/...`` references in the post.
2. If they all point at one folder whose name differs from the post
   slug, suggests renaming that folder to ``/images/<post-slug>/`` and
   rewriting the in-post references.
3. Dry-run by default. Pass ``--apply`` to actually rename and rewrite.

Usage::

    # See what would change.
    python migrate_post.py --post mongolia-is-running-on-fumes

    # Actually do it.
    python migrate_post.py --post mongolia-is-running-on-fumes --apply

Refuses to operate when:
- The post references multiple legacy folders (manual fix needed).
- The destination folder already exists (manual merge needed).
- The post can't be found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "CLAUDE.md").exists() and (parent / "src" / "content" / "posts").exists():
            return parent
    raise SystemExit("Could not locate blog repo root.")


def find_post_file(root: Path, slug: str) -> Path:
    md = root / "src" / "content" / "posts" / f"{slug}.md"
    mdx = root / "src" / "content" / "posts" / f"{slug}.mdx"
    if mdx.exists():
        return mdx
    if md.exists():
        return md
    raise SystemExit(f"Post not found: {slug} (looked for .md and .mdx).")


# Match any /images/<folder>/ reference. Captures the folder name.
IMAGE_REF_RE = re.compile(r"/images/([a-zA-Z0-9_\-]+)(/[^\s\"')\]]+)?")


def find_image_folders(post_text: str) -> dict[str, list[str]]:
    """Return {folder_name: [path1, path2, ...]} for all /images/X refs in the post."""
    folders: dict[str, list[str]] = {}
    for m in IMAGE_REF_RE.finditer(post_text):
        folder = m.group(1)
        full = m.group(0)
        folders.setdefault(folder, []).append(full)
    return folders


def main() -> int:
    p = argparse.ArgumentParser(description="Migrate a legacy image folder to match the post slug.")
    p.add_argument("--post", required=True, help="Post slug (without extension).")
    p.add_argument("--apply", action="store_true", help="Actually perform the rename and rewrite. Default is dry-run.")
    args = p.parse_args()

    root = project_root()
    post_path = find_post_file(root, args.post)
    text = post_path.read_text()

    folders = find_image_folders(text)
    if not folders:
        print(f"No /images/ references found in {post_path.name}. Nothing to do.")
        return 0

    print(f"Post: {post_path.relative_to(root)}")
    print(f"Image folders referenced:")
    for folder, refs in folders.items():
        marker = "  (matches slug)" if folder == args.post else ""
        print(f"  /images/{folder}/  ({len(refs)} ref{'s' if len(refs) != 1 else ''}){marker}")

    legacy_folders = [f for f in folders if f != args.post]
    if not legacy_folders:
        print(f"\nAll references already use /images/{args.post}/. Nothing to migrate.")
        return 0
    if len(legacy_folders) > 1:
        print(f"\nERROR: post references multiple legacy folders: {legacy_folders}.", file=sys.stderr)
        print(f"This needs a manual fix — pick one canonical folder, then rerun.", file=sys.stderr)
        return 2

    old_folder = legacy_folders[0]
    old_dir = root / "public" / "images" / old_folder
    new_dir = root / "public" / "images" / args.post

    print(f"\nProposed change:")
    print(f"  rename {old_dir.relative_to(root)}/  →  {new_dir.relative_to(root)}/")
    print(f"  rewrite {len(folders[old_folder])} reference(s) in {post_path.name}: ")
    print(f"    /images/{old_folder}/  →  /images/{args.post}/")

    if not old_dir.exists():
        print(f"\nWARNING: source folder doesn't exist: {old_dir}", file=sys.stderr)
        print(f"Will only rewrite references; no rename needed.", file=sys.stderr)
    elif new_dir.exists():
        print(f"\nERROR: destination folder already exists: {new_dir}", file=sys.stderr)
        print(f"Manual merge needed. Aborting.", file=sys.stderr)
        return 2

    if not args.apply:
        print(f"\n(dry-run — no changes made. Re-run with --apply to perform the migration.)")
        return 0

    # Rename folder if it exists.
    if old_dir.exists() and not new_dir.exists():
        old_dir.rename(new_dir)
        print(f"renamed: {old_dir.name} → {new_dir.name}")

    # Rewrite references in the post.
    new_text = text.replace(f"/images/{old_folder}/", f"/images/{args.post}/")
    if new_text == text:
        print(f"WARNING: no rewrites applied (substring not found verbatim).", file=sys.stderr)
    else:
        post_path.write_text(new_text)
        print(f"rewrote: {post_path.relative_to(root)}")

    print(f"\nDone. Run `git diff` to review and `git add -p` to stage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
