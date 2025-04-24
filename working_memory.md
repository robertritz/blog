# Docker Build Issue

The build consistently fails with:
```
[vite:load-fallback] Could not load /app/src/layouts/main.astro (imported by src/pages/404.astro): ENOENT: no such file or directory, open '/app/src/layouts/main.astro'
```
This indicates an issue resolving the `~/layouts/main.astro` path alias during the remote Docker build, despite configurations in `vite.config.js` and `astro.config.mjs`.

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
6. Added alias config directly to `astro.config.mjs` using `path.resolve(process.cwd(), "src")`.

## Current Strategy:

1. Kept `src/pages/404.astro` using the path alias `~/layouts/main.astro`
2. **Modified alias config in `astro.config.mjs`**: Changed resolution from `path.resolve(process.cwd(), "src")` to `path.resolve("./src")`.

   ```javascript
   import path from "path"
   // ... other imports

   export default defineConfig({
     // ... other config
     vite: {
       plugins: [tailwindcss()],
       resolve: {
         alias: {
           "~": path.resolve("./src"), // Use relative resolution from config file location
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

Rationale: `process.cwd()` might behave unpredictably in the remote build environment. Using `path.resolve("./src")` resolves the path relative to the `astro.config.mjs` file itself, which should be more stable as its location (`/app/astro.config.mjs`) within the container is fixed after the `COPY . .` step.
