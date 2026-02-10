# YouTube Auto Uploader - Discord Bot
FROM python:3.12-slim

# 作業ディレクトリ
WORKDIR /app

# システム依存関係
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコピー
COPY . .

# ディレクトリ作成
RUN mkdir -p output/discord_data output/discord_videos output/videos

# 権限設定
RUN chmod +x entrypoint.sh || true

# エントリポイント
CMD ["python", "src/discord_bot.py"]
