#!/usr/bin/env bash
# 在 macOS/Linux 上触发 GitHub Actions 自动构建 Windows 安装包
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
  echo "未安装 GitHub CLI (gh)。"
  echo "安装: brew install gh"
  echo "登录: gh auth login"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "初始化 Git 仓库..."
  git init
  git branch -M main
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "尚未配置 Git 远程仓库。"
  echo "请先创建 GitHub 仓库并执行:"
  echo "  git remote add origin https://github.com/<user>/pdfToPic.git"
  exit 1
fi

echo "提交并推送代码..."
git add -A
if git diff --cached --quiet; then
  echo "没有新的更改需要提交。"
else
  git commit -m "chore: trigger Windows installer build"
fi

git push -u origin main

echo "触发 GitHub Actions 构建..."
gh workflow run "Build Windows Installer"

echo ""
echo "构建已触发。查看进度:"
echo "  gh run list --workflow=build-windows.yml"
echo ""
echo "构建完成后下载安装包:"
echo "  gh run download --name PdfToPic-Windows-Installer -D ./installer/output"
