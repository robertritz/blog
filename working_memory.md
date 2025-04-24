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

## Second solution attempt (failed):

Directly modified the import statement in the 404.astro file to use a relative path instead of the path alias:

```
RUN sed -i 's|import MainLayout from "~/layouts/main.astro"|import MainLayout from "../layouts/main.astro"|g' src/pages/404.astro
```

This failed with:

```
Could not resolve "../layouts/main.astro" from "src/pages/404.astro"
```

## Third solution (implemented):

Created a completely new 404.astro file with an absolute path to the layout file:

```bash
RUN echo '---\nimport MainLayout from "/app/src/layouts/main.astro"\n---\n\n<MainLayout title="404" description="Error 404 page not found." noindex={true}>\n  <section class="flex min-h-[60vh] items-center justify-center">\n    <div class="mx-auto max-w-xl px-4 text-center">\n      <h1 class="text-9xl font-bold text-gray-900 dark:text-gray-100">404</h1>\n\n      <div class="mt-4 text-gray-600 dark:text-gray-400">\n        <div class="h2 mb-4">Oops! Page not found</div>\n        <p class="text-lg">\n          The page you are looking for does not exist or has been moved.\n        </p>\n      </div>\n    </div>\n  </section>\n</MainLayout>' > src/pages/404.astro.new && mv src/pages/404.astro.new src/pages/404.astro
```

This approach:
1. Creates a complete new file rather than trying to modify the existing one
2. Uses an absolute path (/app/src/layouts/main.astro) instead of a relative path or alias
3. Keeps the vite.config.js as a backup solution for alias resolution

The key insight is that during Docker builds, paths can be tricky, and sometimes using absolute paths within the container is more reliable.
