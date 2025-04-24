# Docker Build Issue

The build process failed both locally (`npm run dev`) and in Docker (`kamal deploy`) due to issues resolving path aliases (`~/`) after initial attempts to fix them.

## Files checked:

- src/layouts/main.astro - File exists
- tsconfig.json - Has path alias configured: `"~/*": ["./src/*"]`
- .dockerignore - Does not exclude `src/layouts`
- Dockerfile - Uses `COPY . .` which should include the layouts.
- astro.config.mjs - Alias `~` was set to `/app/src`.

## Previous failed attempts:

1. Added a vite.config.js inside Dockerfile to define path aliases
2. Modified import in 404.astro to use relative path `../layouts/main.astro` with sed in Dockerfile
3. Attempted to create a custom 404.astro file with absolute path in Dockerfile
4. Changed import to correct relative path `../../layouts/main.astro` in the codebase
5. Reverted to alias `~/layouts/main.astro` and relied on project's `vite.config.js` copied into Docker
6. Added alias config directly to `astro.config.mjs` using `path.resolve(process.cwd(), "src")`.
7. Modified alias config in `astro.config.mjs` using relative `path.resolve("./src")`.
8. Set alias `~` in `astro.config.mjs` to absolute path `/app/src`.
9. Partially replaced `~/layouts/main.astro` imports with relative paths (missed several other alias usages).

## Current Strategy:

Since alias resolution was consistently problematic, especially in the Docker build, the approach is to eliminate alias usage entirely for `.astro` imports.

1.  **Removed All `~/` Alias Usage in `.astro` files:** Performed a global search for `from "~/` in `src/**/*.astro` and replaced all instances with the corresponding relative paths.
2.  **Removed Alias Config from `astro.config.mjs`:** Removed the `vite.resolve.alias` configuration as it's no longer needed for Astro components/pages.
3.  **Kept Alias Config in `tsconfig.json`:** The alias in `tsconfig.json` (`"~/*": ["./src/*"]`) might still be used by TS/JS files or tooling, so it was left untouched for now.
4.  **Kept Dockerfile:** No changes to Dockerfile.

Rationale: Completely removing alias usage for Astro file imports avoids any ambiguity or environment-specific issues with path resolution during build or dev.

**Next Step**: Retry `npm run dev` locally first. If successful, retry `kamal deploy`.
