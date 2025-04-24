# Astro Air

A minimalism, personal blog theme for Astro.

## Configuration

- Open `src/config/index.ts` and customize your site settings
- Open `src/config/links.ts` and customize your site links
- Open `src/config/en(mn)/about.mdx(intro.mdx、links.mdx)` and customize your pages content

## Writing Content

1. Create new blog posts in one of these directories based on the language:
   - English posts: `src/content/posts/en/`
   - Mongolian posts: `src/content/posts/mn/`

2. Create your post as a Markdown file (`.md`) with the following frontmatter:

```markdown
---
# Required fields
title: "Your Post Title"
author: "Your Name"
pubDate: "YYYY-MM-DD"
description: "A brief description of your post"

# Optional fields
excerpt: "A brief excerpt of your post (if different from description)"
translationId: "unique-id-for-translations"
updatedDate: "YYYY-MM-DD"
tags: ["tag1", "tag2"]
ogImage: "cover image URL"
---

Your content here...
```

The frontmatter section must be at the top of the file between `---` markers. After the frontmatter, write your post content using Markdown formatting.
