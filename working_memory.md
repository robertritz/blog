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

## Solution implemented:
Added a vite.config.js file to the Dockerfile that explicitly defines the path alias:

```javascript
import { defineConfig } from "vite";
import path from "path";
export default defineConfig({
  resolve: {
    alias: {
      "~": path.resolve("./src")
    }
  }
});
```

This will help Vite properly resolve the `~` path alias during the build process in the Docker container.
