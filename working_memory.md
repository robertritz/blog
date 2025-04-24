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

## Previous solutions (failed):

1. Added a vite.config.js inside Dockerfile to define path aliases
2. Modified import in 404.astro to use relative path with sed in Dockerfile
3. Attempted to create a custom 404.astro file with absolute path in Docker

## Final solution (successful):

1. **Fixed the project code directly** rather than trying to modify it in the Dockerfile
2. Changed the import in 404.astro from path alias to relative path:

   ```diff
   ---
   - import MainLayout from "~/layouts/main.astro"
   + import MainLayout from "../layouts/main.astro"
   ---
   ```

3. Added a vite.config.js to the root project to handle path aliases properly:

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

4. Simplified the Dockerfile to remove custom file modifications

This approach is better because:

- It fixes the issue at the source rather than working around it in the build
- It's more maintainable as the fix is part of the codebase
- It properly handles path aliases with the vite.config.js file in the project
