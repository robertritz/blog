# Docker Build Issue

The build is failing with the error:

```
[vite]: Rollup failed to resolve import "~/layouts/main.astro" from "/app/src/pages/404.astro".
```

The issue appears to be with the path alias `~` which is defined in `tsconfig.json` but might not be properly recognized during the Docker build process.

## Files checked:

- src/pages/404.astro - Uses import from "~/layouts/main.astro"
- src/layouts/main.astro - File exists
- tsconfig.json - Has path alias configured: `"~/*": ["./src/*"]`
- astro.config.mjs - Doesn't have explicit alias configuration

## First solution attempt (failed):
Added a vite.config.js file to the Dockerfile that explicitly defines the path alias:

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

This was not enough as the error persisted.

## Second solution (implemented):
Directly modified the import statement in the 404.astro file to use a relative path instead of the path alias:

```
RUN sed -i 's|import MainLayout from "~/layouts/main.astro"|import MainLayout from "../layouts/main.astro"|g' src/pages/404.astro
```

This should replace the problematic import with a direct relative path that doesn't require path alias resolution. We're still keeping the vite.config.js creation as a backup solution.

The key insight is that during the Docker build process, the path alias resolution might not work properly, so directly modifying the import to use a relative path solves the issue without relying on path alias resolution.
