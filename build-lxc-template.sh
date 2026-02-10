#!/bin/bash
# LXCテンプレート作成スクリプト
# このスクリプトは、アプリケーション全体を含むLXCテンプレートを作成します

set -e

echo "🔧 YouTube Auto Uploader - LXCテンプレート作成"
echo "================================================"

# 変数
TEMPLATE_NAME="youtube-uploader-v1.0"
BUILD_DIR="/tmp/lxc-template-build"
ROOTFS="${BUILD_DIR}/rootfs"

# クリーンアップ
echo "📁 作業ディレクトリをクリーンアップ..."
rm -rf ${BUILD_DIR}
mkdir -p ${ROOTFS}

# ベースシステムの準備
echo "📦 ベースシステムをインストール..."
debootstrap noble ${ROOTFS} http://archive.ubuntu.com/ubuntu/

# アプリケーションのセットアップ
echo "📂 アプリケーションファイルをコピー..."
mkdir -p ${ROOTFS}/opt/youtube-uploader

# 必要なファイルのみをコピー
cp -r src ${ROOTFS}/opt/youtube-uploader/
cp -r config ${ROOTFS}/opt/youtube-uploader/
cp -r templates ${ROOTFS}/opt/youtube-uploader/
cp requirements.txt ${ROOTFS}/opt/youtube-uploader/
cp docker-compose.yml ${ROOTFS}/opt/youtube-uploader/
cp Dockerfile ${ROOTFS}/opt/youtube-uploader/
cp .env.example ${ROOTFS}/opt/youtube-uploader/

# セットアップスクリプトを作成
cat > ${ROOTFS}/opt/youtube-uploader/setup.sh << 'SCRIPT_EOF'
#!/bin/bash
set -e

echo "🚀 YouTube Auto Uploader セットアップ"

# Dockerインストール
if ! command -v docker &> /dev/null; then
    echo "📦 Dockerをインストール中..."
    apt-get update
    apt-get install -y ca-certificates curl gnupg
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

cd /opt/youtube-uploader

# .envファイルのセットアップチェック
if [ ! -f .env ]; then
    echo "⚠️  .envファイルが見つかりません"
    echo "📝 .env.exampleを.envにコピーしてください"
    cp .env.example .env
    echo ""
    echo "次のコマンドで編集してください:"
    echo "  nano /opt/youtube-uploader/.env"
    echo ""
    exit 1
fi

# ビルドと起動
echo "🔨 Dockerイメージをビルド中..."
docker compose build

echo "🚀 コンテナを起動中..."
docker compose up -d

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "📊 ステータス確認:"
echo "  docker compose ps"
echo ""
echo "📋 ログ確認:"
echo "  docker compose logs -f"
SCRIPT_EOF

chmod +x ${ROOTFS}/opt/youtube-uploader/setup.sh

# systemdサービスの作成（自動起動用）
cat > ${ROOTFS}/etc/systemd/system/youtube-uploader.service << 'SERVICE_EOF'
[Unit]
Description=YouTube Auto Uploader Discord Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/youtube-uploader
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# 初回起動スクリプト
cat > ${ROOTFS}/root/first-boot.sh << 'FIRSTBOOT_EOF'
#!/bin/bash
echo "🎉 YouTube Auto Uploader コンテナへようこそ！"
echo ""
echo "📝 セットアップ手順:"
echo ""
echo "1. 環境変数を設定:"
echo "   nano /opt/youtube-uploader/.env"
echo ""
echo "2. YouTube認証ファイルを配置:"
echo "   # ローカルPCから:"
echo "   scp client_secret.json root@THIS_IP:/opt/youtube-uploader/"
echo ""
echo "3. セットアップを実行:"
echo "   cd /opt/youtube-uploader"
echo "   ./setup.sh"
echo ""
FIRSTBOOT_EOF

chmod +x ${ROOTFS}/root/first-boot.sh

# rc.localで初回起動メッセージ
cat > ${ROOTFS}/etc/rc.local << 'RCLOCAL_EOF'
#!/bin/bash
/root/first-boot.sh
exit 0
RCLOCAL_EOF

chmod +x ${ROOTFS}/etc/rc.local

# パッケージング
echo "📦 テンプレートをパッケージング中..."
cd ${BUILD_DIR}
tar czf /tmp/${TEMPLATE_NAME}.tar.gz -C rootfs .

# 完了
echo ""
echo "✅ テンプレート作成完了！"
echo ""
echo "📍 作成されたファイル:"
echo "   /tmp/${TEMPLATE_NAME}.tar.gz"
echo ""
echo "📤 次のステップ:"
echo "1. テンプレートをProxmoxにアップロード:"
echo "   scp /tmp/${TEMPLATE_NAME}.tar.gz root@PROXMOX_IP:/var/lib/vz/template/cache/"
echo ""
echo "2. Proxmox Web UIで:"
echo "   - Create CT"
echo "   - Template タブで「${TEMPLATE_NAME}」を選択"
echo "   - コンテナ作成"
echo ""
