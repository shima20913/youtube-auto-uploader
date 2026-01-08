# セットアップガイド

このガイドでは、YouTube自動投稿システムのセットアップ手順を説明します。

## 📋 前提条件

- Googleアカウント
- GitHubアカウント
- Discordサーバー(通知用)

## 🔑 1. APIキーの取得

### 1.1 Gemini API

1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. 「Create API Key」をクリック
3. APIキーをコピーして保存

### 1.2 YouTube Data API v3

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成
3. 「APIとサービス」→「ライブラリ」から「YouTube Data API v3」を検索
4. 「有効にする」をクリック
5. 「認証情報」→「認証情報を作成」→「OAuth クライアント ID」
6. アプリケーションの種類: 「デスクトップアプリ」
7. `client_secret.json`をダウンロード

### 1.3 Pexels API

1. [Pexels API](https://www.pexels.com/api/)にアクセス
2. 無料アカウントを作成
3. APIキーを取得

### 1.4 Discord Webhook

1. Discordサーバーの設定を開く
2. 「連携サービス」→「ウェブフック」
3. 「新しいウェブフック」をクリック
4. 通知先のチャンネルを選択
5. Webhook URLをコピー

## 🚀 2. ローカルセットアップ

### 2.1 リポジトリのクローン

```bash
git clone <your-repository-url>
cd youtube-auto-uploader
```

### 2.2 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集:

```env
GEMINI_API_KEY=your_gemini_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
```

### 2.3 YouTube認証情報の配置

ダウンロードした`client_secret.json`をプロジェクトルートに配置:

```bash
cp ~/Downloads/client_secret.json .
```

### 2.4 依存関係のインストール

```bash
# 仮想環境を作成(推奨)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 2.5 ImageMagickのインストール

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install imagemagick
```

**macOS:**
```bash
brew install imagemagick
```

**Windows:**
[ImageMagick公式サイト](https://imagemagick.org/script/download.php)からインストーラーをダウンロード

## 🧪 3. テスト実行

### 3.1 各モジュールのテスト

```bash
cd src

# コンテンツ生成テスト
python content_generator.py horror

# 音声合成テスト
python tts_engine.py horror

# 素材管理テスト
python asset_manager.py horror
```

### 3.2 エンドツーエンドテスト

```bash
# テストモード(YouTubeにアップロードしない)
python main.py --test --genre horror
```

初回実行時、ブラウザが開いてYouTubeの認証を求められます:
1. Googleアカウントでログイン
2. アクセスを許可
3. `token.pickle`が自動生成されます

### 3.3 実際のアップロードテスト

```bash
# 実際にYouTubeにアップロード
python main.py --genre trivia
```

## ☁️ 4. GitHub Actionsの設定

### 4.1 リポジトリシークレットの設定

GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」で以下を追加:

| シークレット名 | 値 |
|------------|---|
| `GEMINI_API_KEY` | Gemini APIキー |
| `PEXELS_API_KEY` | Pexels APIキー |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL |
| `YOUTUBE_CLIENT_SECRET` | `client_secret.json`の内容全体 |

**YOUTUBE_CLIENT_SECRETの設定方法:**

```bash
# client_secret.jsonの内容をコピー
cat client_secret.json
```

内容全体をコピーしてシークレットに貼り付け

### 4.2 YouTube認証トークンの初回設定

GitHub Actionsでは初回認証が難しいため、ローカルで生成した`token.pickle`をリポジトリに追加:

```bash
# ローカルでtoken.pickleを生成
python src/main.py --test --genre horror

# token.pickleをリポジトリに追加
git add token.pickle
git commit -m "Add YouTube auth token"
git push
```

> ⚠️ **セキュリティ注意**: `token.pickle`は認証情報を含むため、プライベートリポジトリで管理してください

### 4.3 ワークフローの有効化

1. GitHubリポジトリの「Actions」タブを開く
2. ワークフローを有効化
3. 「Run workflow」で手動実行してテスト

## 📅 5. スケジュール設定の確認

`.github/workflows/upload.yml`で設定されているスケジュール:

- **12:00 JST** (毎日)
- **18:00 JST** (毎日)

変更する場合は、cronの時刻を編集してください(UTC時刻で指定):

```yaml
schedule:
  - cron: '0 3 * * *'   # 12:00 JST
  - cron: '0 9 * * *'   # 18:00 JST
```

## 🔧 6. トラブルシューティング

### YouTube API制限エラー

**症状**: `quotaExceeded`エラー

**解決策**:
1. [Google Cloud Console](https://console.cloud.google.com/)で割り当てを確認
2. 初期制限は1日6本まで
3. 制限緩和申請を提出(審査に数週間)

### MoviePyエラー

**症状**: `IMAGEMAGICK_BINARY`エラー

**解決策**:
```python
# video_creator.pyの先頭に追加
import os
os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
```

### Discord通知が届かない

**症状**: 通知が送信されない

**解決策**:
1. Webhook URLが正しいか確認
2. チャンネルの権限を確認
3. テスト実行:
```bash
python src/discord_notifier.py success
```

## 📊 7. 運用のベストプラクティス

### コンテンツの品質管理

- 定期的にアップロードされた動画を確認
- 視聴者のフィードバックに基づいてプロンプトを調整
- `templates/`のプロンプトを改善

### APIクォータ管理

- YouTube API使用量を監視
- 必要に応じて投稿頻度を調整

### バックアップ

- 定期的に`token.pickle`をバックアップ
- 生成された動画を保存(オプション)

## 🎉 完了!

セットアップが完了しました!システムは自動的に1日2回、YouTubeショート動画を生成・投稿します。

何か問題が発生した場合は、Discordに通知が送信されます。
