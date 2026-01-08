# Google Cloud Text-to-Speech API キー取得方法

## 📝 手順

### 1. Google Cloud Consoleにアクセス

[Google Cloud Console](https://console.cloud.google.com/)を開きます。

### 2. プロジェクトを選択または作成

- 既存のプロジェクト(Gemini APIで使用しているもの)を使用できます
- または、新しいプロジェクトを作成します

### 3. Cloud Text-to-Speech APIを有効化

1. 左側のメニューから「**APIとサービス**」→「**ライブラリ**」を選択
2. 検索バーで「**Cloud Text-to-Speech API**」を検索
3. 「**Cloud Text-to-Speech API**」をクリック
4. 「**有効にする**」ボタンをクリック

### 4. APIキーを作成

#### 方法1: APIキーを使用(簡単)

1. 「**APIとサービス**」→「**認証情報**」を選択
2. 「**認証情報を作成**」→「**APIキー**」をクリック
3. APIキーが生成されるのでコピー
4. (推奨)「**キーを制限**」をクリックして、使用するAPIを制限:
   - 「**APIキーの制限**」→「**APIを制限**」
   - 「**Cloud Text-to-Speech API**」を選択
   - 「**保存**」をクリック

#### 方法2: サービスアカウントキーを使用(高度)

1. 「**APIとサービス**」→「**認証情報**」を選択
2. 「**認証情報を作成**」→「**サービスアカウント**」をクリック
3. サービスアカウント名を入力して「**作成**」
4. ロールで「**Cloud Text-to-Speech ユーザー**」を選択
5. 「**完了**」をクリック
6. 作成したサービスアカウントをクリック
7. 「**キー**」タブ→「**鍵を追加**」→「**新しい鍵を作成**」
8. JSON形式を選択して「**作成**」
9. ダウンロードされたJSONファイルを安全な場所に保存

### 5. 環境変数を設定

#### APIキーを使用する場合

`.env`ファイルに以下を追加:

```bash
GOOGLE_CLOUD_TTS_API_KEY=AIzaSy...your_api_key_here
```

#### サービスアカウントキーを使用する場合

`.env`ファイルに以下を追加:

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account-key.json
```

---

## 💰 料金について

### 無料枠
- **月100万文字まで無料**
- このアプリの使用量(1日2本、各300文字 = 月18,000文字)なら**完全無料**

### 有料枠(無料枠超過後)
- **Standard voices**: $4/100万文字
- **WaveNet voices**: $16/100万文字
- **Neural2 voices**: $16/100万文字

このアプリはNeural2を使用していますが、無料枠内で十分運用可能です。

---

## ✅ 確認方法

APIキーが正しく設定されているか確認:

```bash
# 仮想環境を有効化
source venv/bin/activate

# テスト実行
python src/tts_engine.py horror
```

成功すると`test_output.mp3`が生成されます。

---

## 🔧 トラブルシューティング

### エラー: "API key not valid"
- APIキーが正しくコピーされているか確認
- APIキーの制限設定を確認(Cloud Text-to-Speech APIが許可されているか)

### エラー: "API has not been used in project"
- Cloud Text-to-Speech APIが有効化されているか確認
- 数分待ってから再試行

### エラー: "Permission denied"
- サービスアカウントに適切なロールが付与されているか確認
- JSONファイルのパスが正しいか確認
