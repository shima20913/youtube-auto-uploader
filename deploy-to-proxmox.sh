#!/bin/bash
# YouTube Auto Uploader - クイックデプロイスクリプト
# コンテナIP: ***REMOVED***

set -e

echo "📦 YouTube Auto Uploader - デプロイスクリプト"
echo "=============================================="
echo ""

# 変数
CT_IP="***REMOVED***"
PROJECT_DIR="/home/shima09/youtube-auto-uploader"

echo "ステップ1: プロジェクトファイルをアップロード"
echo "----------------------------------------------"
echo "コマンド:"
echo "  cd $PROJECT_DIR"
echo "  scp -r . root@${CT_IP}:/opt/youtube-uploader/"
echo ""
echo "rootパスワードを入力してください"
echo ""

read -p "アップロード完了しましたか? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "アップロードを完了してから再実行してください"
    exit 1
fi

echo ""
echo "ステップ2: コンテナにログインしてDockerセットアップ"
echo "----------------------------------------------------"
echo "次のコマンドを実行してください:"
echo ""
echo "  ssh root@${CT_IP}"
echo ""
echo "コンテナ内で以下を実行:"
echo ""
cat << 'SETUP_SCRIPT'
# システム更新
apt update && apt upgrade -y

# Dockerインストール
apt install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# アプリケーション起動
cd /opt/youtube-uploader
docker compose build
docker compose up -d

# ログ確認
docker compose logs -f
SETUP_SCRIPT

echo ""
echo "=============================================="
echo "セットアップが完了したら、Discordで !ping をテストしてください"
