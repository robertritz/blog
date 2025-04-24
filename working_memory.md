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

---

## Update (2024-04-24):

Deployment still failing with the same error:
`Could not resolve "../layouts/main.astro" from "src/pages/404.astro"`

Hypothesis: Git may not have correctly registered the file rename from `Main.astro` to `main.astro` due to macOS case-insensitivity.

Debugging Steps:

1. Verified the import path `../layouts/main.astro` in `src/pages/404.astro` is correct.
2. Added `RUN ls -la /app/src/layouts` to `Dockerfile` before the `npm run build` step to check the actual file casing inside the Docker container during build.

**Next Step:** Retry `kamal deploy` and examine the output of the new `ls` command in the build logs.

---

## Update (2024-04-24 - Attempt 2):

The `ls -la /app/src/layouts` command in the Docker build log confirmed the file was still named `Main.astro` (uppercase M) inside the container.

**Root Cause:** Git on macOS (case-insensitive) did not properly register the file rename from `Main.astro` to `main.astro` (lowercase m). The import in `src/pages/404.astro` was `../layouts/main.astro`.

**Solution:**

1. Forced Git to recognize the case change using a two-step `git mv` locally:
   ```bash
   git mv src/layouts/Main.astro src/layouts/temp_main.astro
   git mv src/layouts/temp_main.astro src/layouts/main.astro
   ```
2. Committed the change.
3. Removed the temporary `ls` command from the `Dockerfile`.

**Next Step:** Retry `kamal deploy` after committing the forced rename.

---

## Update (2024-04-24 - Attempt 3):

The `git mv` fix resolved the `main.astro` issue.

Deployment now failing with a new error:
`Could not resolve "../../../config/en/about.mdx" from "src/pages/[lang]/about/index.astro"`

Hypothesis: File path, existence, or casing issue with `config/en/about.mdx` inside the Docker container.

Debugging Steps:

1. Verified the import path `../../../config/en/about.mdx` in `src/pages/[lang]/about/index.astro` is correct.
2. Checked `.dockerignore` - `config` directory is not excluded.
3. Added `ls -la /app/src/config` and `ls -la /app/src/config/en` to `Dockerfile` before the `npm run build` step to check the actual file existence and casing inside the Docker container.

**Next Step:** Retry `kamal deploy` and examine the output of the new `ls` commands in the build logs.

---

## Update (2024-04-24 - Attempt 4):

Previous `ls` check failed because it targeted the wrong directory (`/app/config` instead of `/app/src/config`). The build error persists:
`Could not resolve "../../../config/en/about.mdx" from "src/pages/[lang]/about/index.astro"`

The import path correctly points to `/app/src/config/en/about.mdx` within the container.

Hypothesis: File path, existence, or casing issue with `/app/src/config/en/about.mdx` inside the Docker container.

Debugging Steps:
1. Corrected the `ls` commands in `Dockerfile` to check the actual paths used by the import:
   - `ls -la /app/src/config`
   - `ls -la /app/src/config/en`

**Next Step:** Retry `kamal deploy` and examine the output of the corrected `ls` commands in the build logs.
