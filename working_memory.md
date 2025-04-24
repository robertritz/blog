# Docker Build Issue

The build consistently fails with `ENOENT: no such file or directory, open '/app/src/layouts/main.astro'` when trying to load the layout via the `~` alias.

## Files checked:

- src/layouts/main.astro - File exists
- tsconfig.json - Has path alias configured: `"~/*": ["./src/*"]`
- .dockerignore - Does not exclude `src/layouts`
- Dockerfile - Uses `COPY . .` which should include the layouts.
- astro.config.mjs - Verified alias `~` set to `/app/src`.

## Previous failed attempts:

1. Added a vite.config.js inside Dockerfile to define path aliases
2. Modified import in 404.astro to use relative path `../layouts/main.astro` with sed in Dockerfile
3. Attempted to create a custom 404.astro file with absolute path in Dockerfile
4. Changed import to correct relative path `../../layouts/main.astro` in the codebase
5. Reverted to alias `~/layouts/main.astro` and relied on project's `vite.config.js` copied into Docker
6. Added alias config directly to `astro.config.mjs` using `path.resolve(process.cwd(), "src")`.
7. Modified alias config in `astro.config.mjs` using relative `path.resolve("./src")`.
8. Set alias `~` in `astro.config.mjs` to absolute path `/app/src`.

## Current Strategy:

Since alias resolution seems problematic in the Docker build environment (even with absolute paths), reverted to using relative paths for importing `main.astro`.

1.  **Removed Alias Usage:** Changed `import MainLayout from "~/layouts/main.astro"` to use relative paths (`../`, `../../`, `../../../`) in the following files:
    *   `src/pages/[lang]/archive/index.astro`
    *   `src/pages/[lang]/index.astro`
    *   `src/pages/[lang]/about/index.astro`
    *   `src/pages/404.astro`
    *   `src/pages/[lang]/posts/[...slug].astro`
    *   `src/components/astro/tag.astro`
2.  **Kept `astro.config.mjs` alias:** The alias definition `"~": "/app/src"` remains in `astro.config.mjs`, although it's no longer used for `main.astro` imports.
3.  **Kept Dockerfile:** No changes to Dockerfile.

Rationale: Using relative paths bypasses the alias mechanism entirely, which seems to be the source of the inconsistency in the Docker build environment.

**Next Step**: Retry `kamal deploy`.
