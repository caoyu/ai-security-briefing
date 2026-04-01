#!/bin/bash
# AI Security Briefing - Daily Generation Script
# 每日 09:00 自动生成 AI 安全简报
# 使用 GitHub skill: https://github.com/caoyu/ai-security-briefing/blob/main/skills/SKILL.md

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${SCRIPT_DIR}/../ai-security-briefing"
cd "$WORKSPACE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting AI Security Briefing generation..."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Using skill from: ${WORKSPACE}/skills/"

# Step 1: Run tracker.py to collect vendor events (with web_search API)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running tracker.py..."
python3 skills/tracker.py

# Step 2: Get today's date
DATE=$(date '+%Y%m%d')
DATE_DASH=$(date '+%Y-%m-%d')

# Step 3: Commit and push to GitHub
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Checking for changes..."
git add ai-security-${DATE}.html vendor-events-${DATE}.json vendor-snippet.html index.html 2>/dev/null || true

if git diff --cached --quiet; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No changes to commit"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Committing changes..."
    git commit -m "📰 Generate AI Security Briefing ${DATE_DASH}"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pulling latest changes..."
    git pull origin main --no-rebase 2>/dev/null || true
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pushing to GitHub..."
    git push origin main
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Daily briefing generation completed!"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] GitHub Pages: https://caoyu.github.io/ai-security-briefing/"
