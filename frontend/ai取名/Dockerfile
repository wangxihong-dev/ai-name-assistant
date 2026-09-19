# =============================================
# 前端镜像：门户(/) + 取名应用(/app/) + 技术博客(/blog/) + 反向代理 API
#
# 阶段1：node 环境用 uni-app CLI 构建 H5 静态文件
# 阶段2：nginx 托管三样静态内容
#
# ⚠️ 博客不在这个镜像里构建。VitePress 在仓库的 blog/ 目录，
#    而本镜像的构建上下文是 frontend/ai取名，看不到 blog/。
#    所以必须先在本地跑  pwsh blog/stage.ps1  把博客产物拷进 blog-dist/，
#    否则下面那句 COPY blog-dist/ 会直接让构建失败（这是故意的：宁可构建失败，
#    不要静默产出一个没有博客的镜像）。
# =============================================
FROM node:20-alpine AS build
WORKDIR /app

# 国内加速：npm 走国内镜像
RUN npm config set registry https://registry.npmmirror.com

# 先装依赖（利用缓存）
COPY package.json ./
RUN npm install --no-audit --no-fund

# 复制源码，并调整为 uni CLI 需要的 src/ 布局
COPY index.html ./
COPY App.vue main.js pages.json manifest.json uni.scss uni.promisify.adaptor.js /app/src/
COPY pages /app/src/pages
COPY common /app/src/common
COPY vite.config.js ./

# 生产构建：
#  1) API 地址改为同源（""），由 Nginx 统一代理，浏览器无需知道后端地址
#     ⚠️ 这个 sed 是精确字符串匹配。common/api.js 里那一行 BASE_URL 一个字都不能改，
#        改了 sed 匹配不上、不报错，生产环境就会去连浏览器自己的 127.0.0.1:8000
#  2) 修正 HBuilderX 模板与 CLI 构建的入口差异
RUN sed -i 's#const BASE_URL = "http://127.0.0.1:8000"#const BASE_URL = ""#' /app/src/common/api.js \
    && sed -i 's#src="/main.js"#src="/src/main.js"#' /app/index.html \
    && sed -i "s#from './App'#from './App.vue'#" /app/src/main.js \
    && npm run build:h5

# ---------- 运行阶段 ----------
FROM nginx:alpine
# 不放成 default.conf：nginx 官方入口脚本 10-listen-on-ipv6-by-default.sh
# 只在 default.conf 存在时才跑，而且它在处理被替换过的 default.conf 时会卡住。
# 换成自己的文件名再把官方那个删掉，入口脚本就直接跳过，ipv6 监听自己在配置里写。
COPY nginx.conf /etc/nginx/conf.d/app.conf
RUN rm -f /etc/nginx/conf.d/default.conf

# 门户（根路径）
COPY portal/index.html /usr/share/nginx/html/index.html

# 取名应用（/app/）—— base 由 manifest.json 的 h5.router.base 决定
COPY --from=build /app/dist/build/h5 /usr/share/nginx/html/app

# 技术博客（/blog/）—— 由 blog/stage.ps1 预先构建并拷进 blog-dist/
COPY blog-dist/ /usr/share/nginx/html/blog/

EXPOSE 80
