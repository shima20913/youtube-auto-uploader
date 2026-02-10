# Proxmox CT デプロイ手順

このドキュメントでは、YouTube Auto UploaderをProxmox LXCコンテナにデプロイする手順を説明します。

## 前提条件

- Proxmox VE がインストール済み
- 基本的なLinuxコマンドの知識

## ステップ1: LXCコンテナの作成

### 1.1 Proxmox Web UIでコンテナ作成

1. Proxmox Web UIにログイン
2. **Create CT** をクリック
3. 以下の設定を入力：

**General:**
- Hostname: `youtube-uploader`
- Password: 任意のrootパスワード

**Template:**
- Storage: local
- Template: `ubuntu-24.04-standard` または `debian-12-standard`

**Root Disk:**
- Disk size: `20 GB`以上推奨

**CPU:**
- Cores: `2`以上推奨

**Memory:**
- Memory (MiB): `2048`以上推奨
- Swap (MiB): `512`

**Network:**
- Bridge: `vmbr0`
- IPv4: DHCP または Static IP

4. **Finish** → **Start after created** にチェック

### 1.2 コンテナにログイン

```bash
# Proxmoxホストから
pct enter <CT_ID>

# または SSH経由
ssh root@<CT_IP>
```

## ステップ2: Docker環境のセットアップ

### 2.1 システム更新

```bash
apt update && apt upgrade -y
```

### 2.2 Dockerインストール

```bash
# 必要なパッケージ
apt install -y ca-certificates curl gnupg

# Docker公式GPGキー
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Dockerリポジトリ追加
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Dockerインストール
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 動作確認
docker --version
docker compose version
```

## ステップ3: アプリケーションのデプロイ

### 3.1 プロジェクトの配置

```bash
# 作業ディレクトリ作成
mkdir -p /opt/youtube-uploader
cd /opt/youtube-uploader

# Gitからクローン（推奨）
apt install -y git
git clone <YOUR_REPO_URL> .

# または、ローカルからファイルをアップロード
# scp -r /path/to/youtube-auto-uploader root@<CT_IP>:/opt/youtube-uploader/
```

### 3.2 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env
nano .env
```

以下を設定：

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_API_KEY=your_gemini_api_key

# Discord
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_QUESTION_CHANNEL_ID=your_channel_id
DISCORD_WEBHOOK_URL=your_webhook_url
```

### 3.3 YouTube認証ファイルの配置

```bash
# client_secret.jsonをアップロード
# ローカルPCから:
# scp client_secret.json root@<CT_IP>:/opt/youtube-uploader/

# 権限設定
chmod 600 client_secret.json
```

### 3.4 ビルドと起動

```bash
# Dockerイメージをビルド
docker compose build

# コンテナ起動
docker compose up -d

# ログ確認
docker compose logs -f
```

## ステップ4: 動作確認

### 4.1 コンテナステータス確認

```bash
docker compose ps
```

期待される出力：
```
NAME                    STATUS              PORTS
youtube-auto-uploader   Up 2 minutes
```

### 4.2 ログ確認

```bash
# リアルタイムログ
docker compose logs -f discord-bot

# 最新100行
docker compose logs --tail=100 discord-bot
```

### 4.3 Discordでテスト

Discordチャンネルで：
```
!ping
```

Botが応答すれば成功！

## 運用コマンド

### コンテナの管理

```bash
# 起動
docker compose up -d

# 停止
docker compose down

# 再起動
docker compose restart

# ログ確認
docker compose logs -f

# コンテナ内に入る
docker compose exec discord-bot bash
```

### アップデート

```bash
cd /opt/youtube-uploader

# コードを更新（Git使用時）
git pull

# 再ビルドと再起動
docker compose down
docker compose build
docker compose up -d
```

### データのバックアップ

```bash
# 重要なファイルをバックアップ
tar -czf youtube-uploader-backup-$(date +%Y%m%d).tar.gz \
  .env \
  client_secret.json \
  token.json \
  output/
```

## 自動起動設定

### Proxmox CT の自動起動

Proxmox Web UIで：
1. CT を選択
2. **Options** → **Start at boot** → **Yes**

### Docker コンテナの自動起動

`docker-compose.yml` で既に `restart: unless-stopped` が設定済み。

## トラブルシューティング

### コンテナが起動しない

```bash
# ログを確認
docker compose logs

# コンテナを削除して再作成
docker compose down
docker compose up -d
```

### 環境変数が読み込まれない

```bash
# .envファイルを確認
cat .env

# パーミッション確認
ls -la .env

# 再起動
docker compose restart
```

### FFmpegエラー

```bash
# コンテナ内で確認
docker compose exec discord-bot ffmpeg -version
```

## セキュリティ

- `.env` と `client_secret.json` は必ず `.gitignore` に追加
- コンテナはrootで実行されないように設定可能（オプション）
- Proxmox Firewallで不要なポートを閉じる

## パフォーマンス

- CPU: 2コア以上推奨
- RAM: 2GB以上推奨
- Disk: 動画保存のため20GB以上推奨

## サポート

問題が発生した場合：
1. ログを確認: `docker compose logs -f`
2. コンテナステータス: `docker compose ps`
3. 環境変数: `.env` ファイルの内容確認
