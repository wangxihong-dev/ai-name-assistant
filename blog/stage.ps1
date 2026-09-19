# =============================================
# 构建博客，并把产物拷进前端镜像的构建上下文。
#
# 为什么要拷：前端镜像的构建上下文是 frontend/ai取名，
# 看不到仓库根目录的 blog/。所以在 docker build 之前先把产物搬过去。
#
# 用法（在任意目录都行）：
#     pwsh -File blog/stage.ps1
#
# 跑完再执行部署：
#     cd deploy && docker compose up -d --build frontend
# =============================================
$ErrorActionPreference = 'Stop'

$blogDir = $PSScriptRoot
$repo    = Split-Path -Parent $blogDir
$dist    = Join-Path $blogDir 'docs\.vitepress\dist'
$target  = Join-Path $repo 'frontend\ai取名\blog-dist'

Write-Host "1/3 构建博客…" -ForegroundColor Cyan
Push-Location $blogDir
try { npm run build; if ($LASTEXITCODE -ne 0) { throw "vitepress build 失败" } }
finally { Pop-Location }

if (-not (Test-Path -LiteralPath $dist)) { throw "没找到构建产物：$dist" }

Write-Host "2/3 拷到 $target" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item -Path (Join-Path $dist '*') -Destination $target -Recurse -Force

$files = (Get-ChildItem -LiteralPath $target -Recurse -File -Force | Measure-Object).Count
Write-Host "3/3 完成，blog-dist 里现在有 $files 个文件" -ForegroundColor Green
Write-Host ""
Write-Host "注意：Copy-Item -Force 会覆盖同名文件，但不会删掉上次遗留的旧文件。" -ForegroundColor Yellow
Write-Host "如果你删过某篇文章，blog-dist 里它的 html 还会留着。要干净就先手动删掉 blog-dist 整个目录再跑本脚本。" -ForegroundColor Yellow
