# Docker Build Issue

The build is failing with the error:

```
[vite]: Rollup failed to resolve import "~/layouts/main.astro" from "/app/src/pages/404.astro".
```

Issue seems related to path alias (`~`) resolution during the Docker build, even with `vite.config.js` present.

## Files checked:

- src/pages/404.astro - Uses import from "~/layouts/main.astro"
- src/layouts/main.astro - File exists
- tsconfig.json - Has path alias configured: `"~/*": ["./src/*"]`
- astro.config.mjs - Doesn't have explicit alias configuration

## Previous failed attempts:
1. Added a vite.config.js inside Dockerfile to define path aliases
2. Modified import in 404.astro to use relative path `../layouts/main.astro` with sed in Dockerfile
3. Attempted to create a custom 404.astro file with absolute path in Dockerfile
4. Changed import to correct relative path `../../layouts/main.astro` in the codebase

## Current Strategy:
1. Reverted `src/pages/404.astro` to use the path alias `~/layouts/main.astro`
2. Ensured `vite.config.js` exists in the project root with the correct alias definition:
   ```javascript
   import { defineConfig } from "vite"
   import path from "path"
   
   export default defineConfig({
     resolve: {
       alias: {
         "~": path.resolve("./src"),
       },
     },
   })
   ```
3. **Simplified Dockerfile**: Removed the `RUN echo ... > vite.config.js` line. The `COPY . .` command should bring the project's `vite.config.js` into the build context.

Rationale: This approach relies on Astro/Vite correctly picking up the `vite.config.js` from the project files copied into the Docker image, which is the standard way it should work. Overwriting or creating it within the Dockerfile might have caused conflicts.
