# YouTube Auto-Uploader

YouTubeショート動画を自動生成・投稿するシステム

## 機能

- 3つのジャンル(ホラー、雑学、スカッと系)の動画を自動生成
- 1日2回(12時、18時)自動投稿
- Discord通知機能
- 完全無料で運用可能

## セットアップ

### 1. 必要なAPIキーの取得

#### YouTube Data API v3
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成
3. YouTube Data API v3を有効化
4. OAuth 2.0認証情報を作成
5. `client_secret.json`をダウンロード

#### Gemini API
1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. APIキーを作成

#### Pexels API
1. [Pexels API](https://www.pexels.com/api/)にアクセス
2. 無料アカウントを作成
3. APIキーを取得

#### Discord Webhook
1. Discord サーバーの設定 > 連携サービス > ウェブフック
2. 新しいウェブフックを作成
3. Webhook URLをコピー

### 2. 環境変数の設定

```bash
cp .env.example .env
# .envファイルを編集して各APIキーを設定
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. GitHub Actionsの設定

1. GitHubリポジトリのSettings > Secrets and variables > Actions
2. 以下のシークレットを追加:
   - `GEMINI_API_KEY`
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `PEXELS_API_KEY`
   - `DISCORD_WEBHOOK_URL`

## 使い方

### ローカルでテスト実行

```bash
# ホラー系動画を1本生成
python src/main.py --test --genre horror

# 雑学系動画を生成
python src/main.py --test --genre trivia

# スカッと系動画を生成
python src/main.py --test --genre satisfying
```

### GitHub Actionsで自動実行

`.github/workflows/upload.yml`が設定されているため、以下のスケジュールで自動実行されます:
- 毎日12時(JST)
- 毎日18時(JST)

## プロジェクト構造

```
youtube-auto-uploader/
├── .github/workflows/upload.yml    # GitHub Actionsワークフロー
├── src/
│   ├── content_generator.py        # スクリプト生成
│   ├── tts_engine.py               # 音声合成
│   ├── video_creator.py            # 動画生成
│   ├── youtube_uploader.py         # YouTube投稿
│   ├── discord_notifier.py         # Discord通知
│   ├── asset_manager.py            # 素材管理
│   └── main.py                     # メインスクリプト
├── templates/                      # プロンプトテンプレート
├── config/config.yaml              # 設定ファイル
└── requirements.txt                # 依存関係
```

## ライセンス

MIT License

## 注意事項

- YouTube Data API v3には1日のアップロード制限があります(初期は6本/日)
- フリー素材のみを使用し、著作権に注意してください
- YouTubeのコミュニティガイドラインを遵守してください
