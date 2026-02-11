# YouTube Auto Uploader - Discord Bot
FROM python:3.12-slim

# 作業ディレクトリ
WORKDIR /app

# システム依存関係 + Node.js + Remotion(Chromium)用ライブラリ
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-noto-cjk \
    curl \
    ca-certificates \
    gnupg \
    # Remotion/Chromium依存ライブラリ
    chromium \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Node.js 20.x インストール
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコピー
COPY . .

# Remotion npm依存インストール
RUN cd remotion && npm install

# フォントをRemotion公開ディレクトリに配置（gitignoreされているため）
RUN mkdir -p remotion/public/fonts && \
    cp /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc remotion/public/fonts/NotoSansCJKjp-Bold.otf

# ディレクトリ作成
RUN mkdir -p output/discord_data output/discord_videos output/videos

# 権限設定
RUN chmod +x entrypoint.sh || true

# エントリポイント
CMD ["python", "src/discord_bot.py"]
