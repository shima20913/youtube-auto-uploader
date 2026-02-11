#!/bin/bash
# Git-based update script for Proxmox container

echo "🔄 YouTube Auto Uploader - Gitベースのアップデート"
echo "=================================================="

# コンテナ内でgit pullして再起動
ssh root@***REMOVED*** << 'ENDSSH'
pct enter 101 << 'ENDPCT'
cd /opt/youtube-uploader
echo "📥 最新コードを取得中..."
git pull
echo "🔨 Dockerイメージを再ビルド..."
docker compose down
docker compose build
echo "🚀 コンテナを再起動..."
docker compose up -d
echo "✅ アップデート完了!"
docker compose ps
ENDPCT
ENDSSH
