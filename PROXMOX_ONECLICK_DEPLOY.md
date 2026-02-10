# Proxmox ワンクリックデプロイ手順

このガイドでは、カスタムLXCテンプレートを使用して、Proxmox UIからほぼワンクリックでアプリケーションをデプロイする方法を説明します。

## 方法1: カスタムLXCテンプレート（推奨）

### ステップ1: テンプレートの作成（初回のみ）

ローカルPC（このプロジェクトがあるマシン）で実行：

```bash
cd /home/shima09/youtube-auto-uploader

# テンプレート作成スクリプトを実行
chmod +x build-lxc-template.sh
sudo ./build-lxc-template.sh
```

これで `/tmp/youtube-uploader-v1.0.tar.gz` が作成されます。

### ステップ2: Proxmoxにアップロード

```bash
# Proxmoxサーバーにアップロード
scp /tmp/youtube-uploader-v1.0.tar.gz root@<PROXMOX_IP>:/var/lib/vz/template/cache/
```

### ステップ3: Proxmox UIで選択

1. **Proxmox Web UI** にログイン
2. **Create CT** をクリック
3. **Template** タブで `youtube-uploader-v1.0` を選択
4. **CPU/Memory/Network** を設定
5. **Create** をクリック

### ステップ4: 初回セットアップ

コンテナ起動後、コンテナにログイン：

```bash
pct enter <CT_ID>
# または
ssh root@<CT_IP>
```

初回起動メッセージが表示されます。手順に従って：

```bash
# 1. 環境変数を設定
nano /opt/youtube-uploader/.env

# 2. YouTube認証ファイルをアップロード（ローカルPCから）
scp client_secret.json root@<CT_IP>:/opt/youtube-uploader/

# 3. セットアップスクリプトを実行
cd /opt/youtube-uploader
./setup.sh
```

これで完了！

---

## 方法2: シンプルなデプロイ（Docker使用）

テンプレート作成が面倒な場合は、こちらの方法がより簡単です。

### 前提条件

- Proxmoxに Ubuntu 24.04 LXC コンテナを作成済み

### デプロイ手順

#### 1. ワンライナーセットアップスクリプトを作成

```bash
cat > /home/shima09/youtube-auto-uploader/quick-deploy.sh << 'EOF'
#!/bin/bash
# Proxmox CT クイックデプロイスクリプト

set -e

echo "🚀 YouTube Auto Uploader - クイックデプロイ"
echo "============================================="

# Dockerインストール
if ! command -v docker &> /dev/null; then
    echo "📦 Dockerをインストール中..."
    apt-get update
    apt-get install -y ca-certificates curl gnupg git
    
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

# アプリケーションディレクトリ作成
mkdir -p /opt/youtube-uploader
cd /opt/youtube-uploader

# Gitからクローン（ローカルリポジトリの場合はURLを変更）
if [ ! -d ".git" ]; then
    echo "📂 プロジェクトファイルをダウンロード中..."
    # Option 1: Gitリポジトリから
    # git clone <YOUR_REPO_URL> .
    
    # Option 2: ローカルからコピー（手動で実行）
    echo "⚠️  プロジェクトファイルを手動でコピーしてください:"
    echo "   scp -r /home/shima09/youtube-auto-uploader/* root@<THIS_IP>:/opt/youtube-uploader/"
    exit 1
fi

# 環境変数の設定確認
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 .envファイルを作成しました"
    echo "   編集してください: nano .env"
    exit 1
fi

# ビルドと起動
echo "🔨 Dockerイメージをビルド中..."
docker compose build

echo "🚀 コンテナを起動中..."
docker compose up -d

echo ""
echo "✅ デプロイ完了！"
echo ""
echo "📊 ステータス: docker compose ps"
echo "📋 ログ: docker compose logs -f"
EOF

chmod +x /home/shima09/youtube-auto-uploader/quick-deploy.sh
```

#### 2. Proxmoxでコンテナ作成

Proxmox Web UIで普通にUbuntu 24.04 LXCコンテナを作成。

#### 3. プロジェクトファイルをコピー

ローカルPCから：

```bash
# コンテナにファイルをコピー
scp -r /home/shima09/youtube-auto-uploader/* root@<CT_IP>:/opt/youtube-uploader/
```

#### 4. コンテナで実行

```bash
ssh root@<CT_IP>
cd /opt/youtube-uploader
./quick-deploy.sh
```

---

## 方法3: 最も簡単（Web経由）

### Proxmoxホストでプロジェクトを準備

1. **Proxmoxホスト** にSSH接続

2. **プロジェクトをアップロード**

```bash
# Proxmoxホスト上
mkdir -p /var/lib/vz/snippets/youtube-uploader
cd /var/lib/vz/snippets/youtube-uploader

# ローカルPCから
scp -r /home/shima09/youtube-auto-uploader/* root@<PROXMOX_IP>:/var/lib/vz/snippets/youtube-uploader/
```

3. **コンテナ作成後にバインドマウント**

Proxmox Web UIでコンテナ作成後：

```bash
pct set <CT_ID> -mp0 /var/lib/vz/snippets/youtube-uploader,mp=/opt/youtube-uploader
```

これで、ホスト上のファイルがコンテナ内で直接利用可能になります。

---

## まとめ

| 方法 | 難易度 | ワンクリック度 |
|------|--------|----------------|
| カスタムLXCテンプレート | 中 | ⭐⭐⭐⭐⭐ |
| Docker + 手動コピー | 低 | ⭐⭐⭐ |
| バインドマウント | 低 | ⭐⭐⭐⭐ |

**推奨**: 初回は「方法2」で試して、繰り返し使う場合は「方法1」でテンプレート化。
