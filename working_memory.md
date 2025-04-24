## Task: Fix Homepage Title

**Goal:** Change the browser tab title on the homepage from "Robert Ritz - undefined" to "Robert Ritz".

**Actions:**
1. Investigated `src/config/index.ts` - Found `siteName` and `meta.title` set correctly.
2. Investigated `src/layouts/base.astro` - Found the title logic: `{title ? `${config.meta.title} - ${title}` : `${config.meta.title} - ${config.meta.slogan}`}`.
3. Identified that `config.meta.slogan` was undefined, causing the issue on the homepage (where `title` prop is not passed).
4. Modified `src/layouts/base.astro` to use `{title ? `${config.meta.title} - ${title}` : config.meta.title}` instead.

**Result:** Homepage title should now correctly display "Robert Ritz".
