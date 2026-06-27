import type { Metadata, Site, Socials } from "@types"

export const SITE: Site = {
  TITLE: "Robert Ritz",
  DESCRIPTION:
    "The personal site of Robert Ritz, builder and writer. Thirteen years in Mongolia, chasing questions and answering them with data — now writing American Metrics.",
  EMAIL: "robert@aum.edu.mn",
  NUM_POSTS_ON_HOMEPAGE: 6,
  NUM_PROJECTS_ON_HOMEPAGE: 0,
}

export const HOME: Metadata = {
  TITLE: "Robert Ritz",
  DESCRIPTION:
    "Builder and writer. For years I chased questions about Mongolia; now about America too. I answer them with data.",
}

export const BLOG: Metadata = {
  TITLE: "Archive",
  DESCRIPTION: "Every post, newest first.",
}

export const SOCIALS: Socials = [
  {
    NAME: "American Metrics",
    HREF: "https://americanmetrics.org",
  },
  {
    NAME: "X",
    HREF: "https://x.com/RobertERitz",
  },
  {
    NAME: "GitHub",
    HREF: "https://github.com/robertritz",
  },
]
