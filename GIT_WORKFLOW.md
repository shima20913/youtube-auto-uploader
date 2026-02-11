# Git-Based Deployment Workflow

## ✅ セットアップ完了

**GitHubリポジトリ**: `github.com:shima20913/youtube-auto-uploader.git`

## コンテナをGitベースに切り替え

現在のProxmoxコンテナで実行：

```bash
# コンテナにログイン
pct enter 101

# Git インストール
apt install -y git

# 既存ディレクトリをバックアップ
cd /opt
mv youtube-uploader youtube-uploader.bak

# Gitからクローン
git clone https://github.com/shima20913/youtube-auto-uploader.git youtube-uploader

# .envファイルを復元
cp youtube-uploader.bak/.env youtube-uploader/

# 再起動
cd youtube-uploader
docker compose down
docker compose build
docker compose up -d
```

## 今後のアップデート手順

### ローカルで修正
```bash
cd /home/shima09/youtube-auto-uploader

# コード修正...
nano src/discord_bot.py

# コミット & プッシュ
git add .
git commit -m "機能追加"
git push
```

### サーバーで更新
```bash
# コンテナにログイン
pct enter 101

# 更新
cd /opt/youtube-auto-uploader
git pull
docker compose down
docker compose build
docker compose up -d

# 確認
docker compose logs -f
```

## クイック更新スクリプト

新しいファイル [`update-deployment.sh`](file:///home/shima09/youtube-auto-uploader/update-deployment.sh) を作成しました。

今後は：
```bash
# ローカルで修正後
git commit -am "修正内容"
git push

# サーバー更新（手動）
pct enter 101
cd /opt/youtube-auto-uploader && git pull && docker compose down && docker compose build && docker compose up -d
```

これで管理が非常に楽になります！
