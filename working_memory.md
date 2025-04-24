# Docker Build Issue

The build process continues to fail in Docker (`kamal deploy`) due to case sensitivity issues with filenames between macOS (local) and Linux (Docker).

## Files checked:

- src/layouts/Main.astro - File existed with capital 'M'. Imports used lowercase 'm'.
- src/pages/404.astro - Imports `../layouts/main.astro`.
- tsconfig.json - Alias `~` exists but isn't used by `.astro` files.
- .dockerignore - Does not exclude `src/layouts` or `src/styles`.
- Dockerfile - Uses `COPY . .` before `npm run build`. Added temporary `ls` commands.
- astro.config.mjs - Alias `~` was removed.

## Previous failed attempts:

1. Various alias configurations (`vite.config.js`, `astro.config.mjs`, absolute/relative paths).
2. Eliminating alias usage entirely for `.astro` and CSS imports.

## Problem Identification:

- Added `ls -la /app/src/layouts` to Dockerfile before build step.
- Build log showed the file was copied as `Main.astro` (capital M).
- Imports used `main.astro` (lowercase m).
- Linux (Docker) is case-sensitive, macOS (local) is often not.

## Current Strategy:

1.  **Renamed File:** Renamed `src/layouts/Main.astro` to `src/layouts/main.astro` using `mv` to match the import paths and ensure consistency across case-sensitive and case-insensitive filesystems.
2.  **Kept Relative Paths:** All imports remain as relative paths.
3.  **No Alias Config:** `astro.config.mjs` remains without Vite alias config.
4.  **Cleanup Dockerfile:** Removed the temporary `ls` commands from Dockerfile.

Rationale: Aligning the filename casing with the import casing resolves the file resolution error caused by filesystem case sensitivity differences.

**Next Step**: Retry `kamal deploy`.
