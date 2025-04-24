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
5. Reverted to alias `~/layouts/main.astro` and relied on project's `vite.config.js` copied into Docker

## Current Strategy:

1. Kept `src/pages/404.astro` using the path alias `~/layouts/main.astro`
2. **Added alias config directly to `astro.config.mjs`**: 
   ```javascript
   import path from "path"
   // ... other imports
   
   export default defineConfig({
     // ... other config
     vite: {
       plugins: [tailwindcss()],
       resolve: {
         alias: {
           "~": path.resolve(process.cwd(), "src"), // Explicitly resolve from cwd
         },
       },
     },
     integrations: [
       // ... integrations
     ],
   })
   ```
3. Ensured `vite.config.js` still exists in the project root (it might be redundant now, but harmless).
4. Kept the simplified Dockerfile.

Rationale: Centralizing the Vite configuration within `astro.config.mjs` is the most standard Astro approach. Using `path.resolve(process.cwd(), "src")` ensures the path is resolved correctly relative to the project root, even within the potentially complex build environment created by Kamal's remote builder.
