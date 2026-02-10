# YouTubeショート選択式質問動画 自動生成システム

視聴者に選択をゆだねる形式の動画（例：「1週間耐えたら5億円！どの部屋を選ぶ？」）を自動生成・投稿するシステム

## 機能

- **AI生成動画**: LumaAI Ray3.14による高品質な動画生成
- **自動質問生成**: Gemini APIで視聴者参加型の選択式質問を生成
- **1日2回自動投稿**: GitHub Actionsによるスケジュール実行
- **Discord通知**: 投稿結果を自動通知

## セットアップ

### 1. 必要なAPIキーの取得

#### Gemini API（質問生成用）
1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. APIキーを作成

#### LumaAI API（AI動画生成用）
1. [LumaAI](https://lumalabs.ai/)でアカウント作成
2. [API Settings](https://lumalabs.ai/api)でAPIキーを取得
3. 推奨プラン: **Plus Plan** ($29.99/月) - 商用利用可、1080p、10,000クレジット

#### YouTube Data API v3（動画投稿用）
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成
3. YouTube Data API v3を有効化
4. OAuth 2.0認証情報を作成
5. `client_secret.json`をダウンロードしてプロジェクトルートに配置

#### Discord Webhook（通知用）
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

### 4. YouTube認証（初回のみ）

```bash
# テストモードで実行（認証トークンを生成）
python src/main.py --test
# ブラウザが開くのでGoogleアカウントでログイン・許可
```

## 使い方

### ローカルでテスト実行

```bash
# テストモード（YouTubeにアップロードしない）
python src/main.py --test

# カテゴリを指定
python src/main.py --test --category "大金獲得チャレンジ"
python src/main.py --test --category "究極の選択"
python src/main.py --test --category "好みタイプ診断"
```

### 本番実行（YouTube投稿）

```bash
# ランダムカテゴリで投稿
python src/main.py

# カテゴリ指定で投稿
python src/main.py --category "大金獲得チャレンジ"
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
│   ├── question_generator.py      # 質問生成（Gemini API）
│   ├── ai_video_generator.py      # AI動画生成（LumaAI API）
│   ├── video_creator.py           # 動画編集・統合
│   ├── youtube_uploader.py        # YouTube投稿
│   ├── discord_notifier.py        # Discord通知
│   ├── tts_engine.py             # 音声合成（将来拡張用）
│   └── main.py                   # メインスクリプト
├── config/
│   └── video_config.yaml          # 動画設定
├── output/                        # 生成された動画の出力先
└── requirements.txt               # 依存関係
```

## 動画フォーマット

### 構成（30-60秒のYouTubeショート）

1. **オープニング（6秒）**
   - 質問文を大きく表示
   - 補足条件を表示

2. **選択肢1〜4（各8秒）**
   - AI生成された高品質な映像
   - 選択肢番号・タイトル・説明文をオーバーレイ

3. **エンディング（5秒）**
   - 「あなたはどれを選んだ？」
   - 「コメント欄で教えて！」

### 質問カテゴリ

- **大金獲得チャレンジ**: 「〇〇を耐え抜いたら大金がもらえる」系
- **究極の選択**: 日常的な場面での選びにくい選択
- **好みタイプ診断**: 好みや性格が分かる選択肢

## コスト試算

### 月60本投稿の場合（1日2回）

- **LumaAI Plus Plan**: $29.99/月
  - 10,000クレジット/月
  - 1動画 = 4選択肢 × 8秒 = 32秒
  - 月60本 = 約1,920秒の動画生成
  - プラン内で安定運用可能

- **Gemini API**: 無料枠内（月1000リクエスト以下）
- **YouTube API**: 無料
- **Discord Webhook**: 無料

**合計: 約$30/月**

## 注意事項

- YouTube Data API v3には1日のアップロード制限があります（初期は6本/日）
- AI生成動画には時間がかかります（1動画あたり1-3分）
- LumaAI APIの利用制限に注意してください
- YouTubeコミュニティガイドラインを遵守してください

## トラブルシューティング

### LumaAI APIエラー

```bash
# APIキーを確認
echo $LUMAAI_API_KEY

# .envファイルを確認
cat .env
```

### MoviePyエラー

ImageMagickが必要です:

```bash
# Ubuntu/Debian
sudo apt-get install imagemagick

# macOS
brew install imagemagick
```

## ライセンス

MIT License
