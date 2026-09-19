import { defineConfig } from "vitepress"

// base 必须是 '/blog/'：整个站点部署在服务器的 /blog/ 子路径下，
// 少一个斜杠资源就全 404
export default defineConfig({
  base: "/blog/",
  lang: "zh-CN",
  title: "一个应届生的项目笔记",
  description: "AI 取名助手的开发记录，包括我踩过的坑",
  lastUpdated: true,
  // 「回到应用」指向 /app/，那不是 md 文件，不关掉会被当成死链报错
  ignoreDeadLinks: true,
  head: [["meta", { name: "viewport", content: "width=device-width, initial-scale=1" }]],

  themeConfig: {
    nav: [
      { text: "首页", link: "/" },
      { text: "文章", link: "/posts/" },
      { text: "GitHub", link: "https://github.com/wangxihong-dev/ai-name-assistant" }
    ],

    sidebar: {
      "/posts/": [
        {
          text: "全部文章",
          items: [
            { text: "这个项目一半代码是 AI 写的", link: "/posts/ai-wrote-half" },
            { text: "Milvus 被 OOM 杀掉那次", link: "/posts/oom" },
            { text: "我抓到一次 AI 编的出处", link: "/posts/hallucination" },
            { text: "法条存进数据库", link: "/posts/law-as-data" }
          ]
        }
      ]
    },

    outline: { level: [2, 3], label: "这一页" },
    docFooter: { prev: "上一篇", next: "下一篇" },
    lastUpdated: { text: "最后更新" },
    darkModeSwitchLabel: "主题",
    sidebarMenuLabel: "目录",
    returnToTopLabel: "回到顶部",
    socialLinks: [{ icon: "github", link: "https://github.com/wangxihong-dev/ai-name-assistant" }]
  }
})
