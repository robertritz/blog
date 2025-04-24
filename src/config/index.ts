import { Github, Twitter } from "lucide-react"

export const defaultLanguage: string = "en"

export const common = {
  domain: "robertritz.com",
  meta: {
    favicon: "/avatar.png",
    url: "https://robertritz.com",
  },
  googleAnalyticsId: "",
  social: [
    {
      icon: Github,
      label: "GitHub",
      link: "https://github.com/robertritz",
    },
    {
      icon: Twitter,
      label: "X",
      link: "https://x.com/RobertERitz",
    },
  ],
  rss: true,
  navigation: {
    home: true,
    archive: true,
    custom: [],
    links: false,
    about: true,
  },
  latestPosts: 8,
  comments: {
    enabled: false,
    twikoo: {
      enabled: false,
      envId: "",
    },
  },
}

export const mn = {
  ...common,
  siteName: "Роберт Риц",
  meta: {
    ...common.meta,
    title: "Роберт Риц",
    description: "Роберт Риц",
  },
  navigation: {
    ...common.navigation,
  },
  pageMeta: {
    archive: {
      title: "Бүх нийтлэлүүд",
      description: "Блогийн бүх нийтлэлүүд",
      ogImage: "/images/page-meta/mn/archive.png",
    },
    about: {
      title: "Миний тухай",
      description: "Роберт Риц-ийн танилцуулга",
      ogImage: "/images/page-meta/mn/about.png",
    },
  },
}

export const en = {
  ...common,
  siteName: "Robert Ritz",
  meta: {
    ...common.meta,
    title: "Robert Ritz",
    description: "Robert Ritz",
  },
  navigation: {
    ...common.navigation,
  },
  pageMeta: {
    archive: {
      title: "All Posts",
      description: "All posts",
      ogImage: "/images/page-meta/en/archive.png",
    },
    about: {
      title: "About Me",
      description: "About Robert Ritz",
      ogImage: "/images/page-meta/en/about.png",
    },
  },
}
