# アップデート手順

## 修正してデプロイ

### 1. ローカルで修正
IDEでファイルを編集して保存

### 2. Git push
```bash
git add .
git commit -m "修正内容"
git push
```

### 3. サーバーで更新
```bash
pct enter 101
cd /opt/youtube-auto-uploader && git pull && docker compose down && docker compose build && docker compose up -d
```

## 確認
```bash
docker compose logs -f
```

Discordで `!ping` をテスト

---

## 環境情報
- **Proxmox Host**: ***REMOVED***
- **Container ID**: 101
- **アプリパス**: `/opt/youtube-auto-uploader`
- **リポジトリ**: https://github.com/shima20913/youtube-auto-uploader
