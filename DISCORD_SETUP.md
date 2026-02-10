# Discord Bot セットアップガイド

Discord Bot統合で完全無料運用（Sora 2手動生成）

## 1. Discord Bot作成

### Discord Developer Portalで設定

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」をクリック
3. 名前: 「YouTube Question Bot」（任意）
4. 「Bot」タブ → 「Add Bot」
5. **Bot Token** をコピー（後で`.env`に設定）

### 必要な権限設定

「Bot」タブで以下を有効化:
- ✅ MESSAGE CONTENT INTENT（重要！）
- ✅ SERVER MEMBERS INTENT

「OAuth2」→「URL Generator」で権限選択:
- Scopes: `bot`
- Bot Permissions:
  - ✅ Send Messages
  - ✅ Send Messages in Threads
  - ✅ Create Public Threads
  - ✅ Attach Files
  - ✅ Read Message History
  - ✅ Add Reactions

生成されたURLをブラウザで開き、Botをサーバーに招待

---

## 2. チャンネルID取得

1. Discordで「開発者モード」を有効化
   - 設定 → アプリの設定 → 詳細設定 → 開発者モード ON

2. お題を投稿したいチャンネルを右クリック
3. 「IDをコピー」

---

## 3. 環境変数設定

```bash
cp .env.example .env
nano .env
```

`.env`ファイルに追加:

```env
# Discord Bot Token（Developer Portalからコピー）
DISCORD_BOT_TOKEN=MTE1NDIyNzg4MTk2OTk0MDQ4.GxXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Discord Question Channel ID（右クリックでコピー）
DISCORD_QUESTION_CHANNEL_ID=123456789012345678

# Discord Webhook URL（通知用・既存）
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

---

## 4. 依存関係インストール

```bash
pip install -r requirements.txt
```

---

## 5. Bot起動

### ローカルで起動（テスト）

```bash
cd /home/shima09/youtube-auto-uploader
python src/discord_bot.py
```

出力例:
```
🤖 Discord Bot を起動しています...
Ctrl+C で終了
✅ Discord Bot起動: YouTube Question Bot
チャンネルID: 123456789012345678
```

### バックグラウンドで常駐（tmux）

```bash
# tmuxセッション作成
tmux new -s youtube-bot

# Bot起動
python src/discord_bot.py

# デタッチ（Ctrl+B → D）

# 再アタッチ
tmux attach -t youtube-bot
```

---

## 6. 使い方

### 自動投稿（毎日19:00）

Botが自動的に:
1. お題を生成
2. Discordチャンネルに投稿
3. スレッド作成

### 手動で動画投稿

1. スレッドを開く
2. Sora 2で生成した **4本の動画** を選択
3. スレッドにドラッグ&ドロップ
4. 送信

→ **Botが自動検知 → 統合 → YouTube投稿！**

### コマンド

```
!test      # テスト用お題を投稿
!status    # 現在の進捗確認
!reset     # スレッドをリセット
```

---

## 7. トラブルシューティング

### Bot がメッセージに反応しない

→ **MESSAGE CONTENT INTENT** が有効か確認

### チャンネルが見つからない

→ チャンネルIDが正しいか確認（数字のみ）

### Bot が起動しない

```bash
# トークンを確認
cat .env | grep DISCORD_BOT_TOKEN
```

---

## 8. クラウドで常駐（オプション）

ローカルPCを常時起動したくない場合:

### Railway.app（無料枠あり）

1. [Railway.app](https://railway.app/) でアカウント作成
2. 「New Project」→「Deploy from GitHub repo」
3. 環境変数を設定
4. 自動デプロイ

### Render.com（無料枠あり）

1. [Render.com](https://render.com/) でアカウント作成
2. 「New Background Worker」
3. Start Command: `python src/discord_bot.py`

---

## ワークフロー全体

```
[19:00 自動]
  Bot → お題投稿 + スレッド作成

[あなた]
  ↓
  Sora 2 で4本生成（10-20分）
  ↓
  スレッドに4本投稿（30秒）

[Bot 自動]
  ↓
  検知 → 統合 → YouTube投稿 → 完了通知
```

---

## 完了！

これで完全無料（AI API料金ゼロ）でSora 2の最高品質動画をYouTubeに自動投稿できます。
