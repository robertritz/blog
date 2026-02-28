# Repository Guidelines

## Scope

Personal Astro blog for `robertritz.com`.

## Stack

- Astro
- Tailwind CSS
- Kamal deployment

## Key Paths

- `src/content/posts/` - blog post markdown files
- `src/content.config.ts` - frontmatter schema
- `config/deploy.yml` - Kamal config

## Development

```bash
npm install
npm run dev
npm run build
npm run preview
```

## Deployment

- Kamal deploys from git state; commit before deploy.
- Deploy command:

```bash
kamal deploy
```

## Rules

- Keep URL structure stable (`/posts/<slug>/`, `/archive/`).
- Preserve minimalist style and readable typography.
