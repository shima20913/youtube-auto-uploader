# Remotion Integration - Quick Reference

## 🎬 Remotionプロジェクト構成

```
remotion/
├── src/
│   ├── components/
│   │   └── QuestionTemplate1.tsx   # テンプレート1
│   ├── themes/
│   │   └── daily-themes.ts         # 日替わりテーマ
│   ├── Root.tsx                    # ルートコンポーネント
│   └── index.ts                    # エントリーポイント
├── remotion.config.ts              # Remotion設定
├── tsconfig.json                   # TypeScript設定
└── package.json                    # 依存関係
```

## 🎨 日替わりテーマ

| 曜日 | テーマ | 主色 | アクセント |
|------|--------|------|-----------|
| 月 | Pop | ピンク | 黄色 |
| 火 | Retro | オレンジ | ベージュ |
| 水 | Cool | 青 | 紫 |
| 木 | Natural | 緑 | オレンジ |
| 金 | Elegant | 黒 | 金 |
| 土 | Colorful | 赤 | 青 |
| 日 | Simple | グレー | ライトグレー |

## 📹 動画生成方法

### Python経由（推奨）

```python
from src.remotion_renderer import RemotionRenderer

renderer = RemotionRenderer()
question_data = {
    "id": "001",
    "question": "あなたはどっち派？",
    "options": ["朝型人間", "夜型人間"]
}

renderer.render_question_video(
    question_data,
    "output/question_video.mp4"
)
```

### 直接コマンド

```bash
cd remotion
npx remotion render QuestionTemplate1 output.mp4 \
  --props='{"data":{"id":"001","question":"テスト","options":["A","B"]}}'
```

## 🔧 開発プレビュー

```bash
cd remotion
npm run start
```

ブラウザで `http://localhost:3000` が開きます。

## 🚀 次のステップ

- [ ] カスタムフォント追加
- [ ] テンプレート2, 3作成
- [ ] アニメーションバリエーション拡充
- [ ] Discord Bot統合
