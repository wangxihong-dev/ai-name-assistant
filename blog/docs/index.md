---
layout: home

hero:
  name: 一个应届生的项目笔记
  text: AI 取名助手是怎么做出来的
  tagline: 2027 届 · 西安 · 后端为主，前端是 AI 帮我搞的
  actions:
    - theme: brand
      text: 开始读
      link: /posts/
    - theme: alt
      text: GitHub
      link: https://github.com/wangxihong-dev/ai-name-assistant

features:
  - title: 都是真事
    details: 每篇都有具体的日期、具体的报错原文、具体的数字，你可以自己核。
  - title: 弯路比结论多
    details: 结论谁都能抄。我写的是当时怎么想错的、后来怎么发现的。
  - title: 不懂的地方我会说不懂
    details: 有些地方我到现在也没完全搞明白，那我就写「没搞明白」。
---

## 这个项目是什么

一个取名网站，原来只做人名（诗经楚辞唐诗宋词 + 向量检索），2026 年 9 月开始加品牌／产品取名，
底下垫了一层商标法规则引擎：法条存在数据库里、禁用字样名录 158 条、模型只输出条款编号、
代码拿着编号回表取原文，这样模型没有机会改法条的字。

已经上线了，跑在一台 2 核 4G 的阿里云 ECS 上，六个 Docker 容器。

## 为什么写这个

秋招面试被问过「你这个 agent 是怎么设计的」，我发现自己讲不清楚——不是不会，是那些决定当时做完就忘了为什么。
写下来是逼自己把理由重新捋一遍。

顺便，如果我踩过的坑能让别人少踩一次，那也算有点用。

<div class="go-app">
<a href="/app/" target="_self">去用一下项目 →</a>
</div>

<style>
.go-app { margin-top: 8px; }
.go-app a {
  display: inline-block; padding: 8px 18px; border-radius: 8px;
  background: #2E7D7B; color: #fff !important; font-size: 14px;
  text-decoration: none !important;
}
.go-app a:hover { opacity: .9; }
</style>