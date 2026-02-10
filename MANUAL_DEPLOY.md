# YouTube Auto Uploader - 手動デプロイ手順

## 概要
- **Proxmox Host IP**: ***REMOVED***
- **Container IP**: ***REMOVED***
- **Container ID**: 101

## 手順

### 1. Proxmoxホストにファイルをアップロード

```bash
cd /home/shima09/youtube-auto-uploader
scp -r . root@***REMOVED***:/tmp/youtube-uploader/
# パスワード入力
```

### 2. Proxmoxホストにログイン

```bash
ssh root@***REMOVED***
```

### 3. ファイルをコンテナにコピー

Proxmoxホスト上で：

```bash
pct push 101 /tmp/youtube-uploader /opt/youtube-uploader -r
```

### 4. コンテナにログイン

```bash
pct enter 101
```

### 5. Dockerセットアップ（コンテナ内）

```bash
# システム更新
apt update && apt upgrade -y

# Dockerインストール
apt install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 6. アプリケーション起動

```bash
cd /opt/youtube-uploader

# ビルド
docker compose build

# 起動
docker compose up -d

# ログ確認
docker compose logs -f
```

### 7. 動作確認

Discordで：
```
!ping
!test
```

## トラブルシューティング

### ログ確認
```bash
docker compose logs -f
```

### 再起動
```bash
docker compose restart
```

### コンテナ停止
```bash
docker compose down
```

## 補足

- `client_secret.json` がない場合、YouTube連携は動作しません
- Discord Botは動作します
- 後から `client_secret.json` を追加可能
