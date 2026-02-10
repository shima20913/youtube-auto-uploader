"""
選択式質問生成モジュール
Gemini APIを使用して視聴者参加型の選択式質問を生成
"""

import json
import random
import os
from typing import Dict, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class QuestionGenerator:
    """選択式質問生成クラス"""
    
    def __init__(self):
        """初期化"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')

        
        # 安全性設定（不適切コンテンツをブロック）
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # カテゴリ定義
        self.categories = self._load_categories()
    
    def _load_categories(self) -> List[Dict]:
        """カテゴリ定義をロード"""
        return [
            {
                "name": "大金獲得チャレンジ",
                "prompt_template": """
あなたは視聴者参加型のYouTubeショート動画のシナリオライターです。
以下の条件で、選択式質問を生成してください。

【テーマ】
「〇〇を耐え抜いたら大金がもらえる」という設定

【要件】
1. 質問文: キャッチーで興味を引く質問（例: 「1週間耐えたら5億円！どの部屋を選ぶ？」）
2. 補足条件: 1つの短い注意事項（例: 「※1週間外出禁止です！」）
3. 選択肢: 4つの異なる厳しい環境や条件を提示
4. 各選択肢の特徴:
   - どれも選びにくいが、完全に不可能ではない
   - それぞれ異なる種類の過酷さ（physical, mental, social etc.）
   - リアルで想像しやすい状況
5. YouTube規約準拠: 暴力的、性的、差別的な内容は一切含めない

【出力形式】
以下のJSON形式で出力してください：
{
  "question": "キャッチーな質問文",
  "context": "補足条件（※付き）",
  "reward": "報酬額",
  "choices": [
    {
      "number": 1,
      "title": "選択肢のタイトル（5文字以内）",
      "description": "詳細説明（15文字程度）",
      "video_prompt": "AI動画生成用の英語プロンプト（詳細かつ視覚的な描写、cinematic style）"
    },
    ... 4つの選択肢
  ]
}

それでは生成してください。JSON形式のみを出力し、他の説明は不要です。
"""
            },
            {
                "name": "究極の選択",
                "prompt_template": """
あなたは視聴者参加型のYouTubeショート動画のシナリオライターです。
以下の条件で、選択式質問を生成してください。

【テーマ】
日常的な場面での「究極の選択」

【要件】
1. 質問文: 親しみやすく共感を呼ぶ質問（例: 「一生使えるのはどっち？」）
2. 補足条件: シンプルな1文の前提条件
3. 選択肢: 4つの選び にくい選択肢
4. 各選択肢の特徴:
   - どれもメリット・デメリットがある
   - 日常生活に関連
   - 視聴者が自分事として考えられる
5. YouTube規約準拠: 暴力的、性的、差別的な内容は一切含めない

【出力形式】
以下のJSON形式で出力してください：
{
  "question": "質問文",
  "context": "補足条件",
  "choices": [
    {
      "number": 1,
      "title": "選択肢タイトル",
      "description": "詳細説明",
      "video_prompt": "AI動画生成用の英語プロンプト（視覚的で魅力的な描写）"
    },
    ... 4つの選択肢
  ]
}

JSON形式のみを出力してください。
"""
            },
            {
                "name": "好みタイプ診断",
                "prompt_template": """
あなたは視聴者参加型のYouTubeショート動画のシナリオライターです。
以下の条件で、選択式質問を生成してください。

【テーマ】
好みや性格が分かる選択肢

【要件】
1. 質問文: 「あなたの好みは？」系の質問
2. 補足条件: 簡潔な1文
3. 選択肢: 4つの異なる好み・タイプ
4. 各選択肢の特徴:
   - それぞれ明確に異なる個性
   - ポジティブな表現
   - 視聴者が自分を投影できる
5. YouTube規約準拠: 暴力的、性的、差別的な内容は一切含めない

【出力形式】
以下のJSON形式で出力してください：
{
  "question": "質問文",
  "context": "補足条件",
  "choices": [
    {
      "number": 1,
      "title": "選択肢タイトル",
      "description": "詳細説明",
      "video_prompt": "AI動画生成用の英語プロンプト（美しく魅力的な描写）"
    },
    ... 4つの選択肢
  ]
}

JSON形式のみを出力してください。
"""
            }
        ]
    
    def generate_question(self, category: str = None) -> Dict:
        """
        選択式質問を生成
        
        Args:
            category: カテゴリ名（省略時はランダム）
            
        Returns:
            生成された質問データ
        """
        # カテゴリ選択
        if category:
            selected_category = next(
                (c for c in self.categories if c["name"] == category),
                None
            )
            if not selected_category:
                selected_category = random.choice(self.categories)
        else:
            selected_category = random.choice(self.categories)
        
        # Gemini APIでコンテンツ生成
        prompt = selected_category["prompt_template"]
        
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            content = response.text.strip()
            
            # JSONをパース
            # コードブロックを除去
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            question_data = json.loads(content.strip())
            
            # カテゴリ情報を追加
            question_data["category"] = selected_category["name"]
            
            return question_data
            
        except Exception as e:
            print(f"エラー: {e}")
            # フォールバック: デフォルト質問を返す
            return self._get_fallback_question()
    
    def _get_fallback_question(self) -> Dict:
        """エラー時のフォールバック質問"""
        return {
            "category": "大金獲得チャレンジ",
            "question": "1週間耐えたら1億円！どの部屋を選ぶ？",
            "context": "※1週間外出禁止です！",
            "reward": "1億円",
            "choices": [
                {
                    "number": 1,
                    "title": "極寒の部屋",
                    "description": "氷点下20度の冷凍室",
                    "video_prompt": "A freezing cold room with ice-covered walls, frost everywhere, dim blue lighting, icy atmosphere, cinematic, ultra-realistic, 4k"
                },
                {
                    "number": 2,
                    "title": "灼熱の部屋",
                    "description": "気温50度のサウナ室",
                    "video_prompt": "An extremely hot sauna room, steam rising, wooden walls glowing with heat, sweat dripping, orange warm lighting, cinematic, ultra-realistic, 4k"
                },
                {
                    "number": 3,
                    "title": "完全暗闇",
                    "description": "光が一切ない真っ暗な部屋",
                    "video_prompt": "A pitch black dark room, complete darkness, only faint shadows, eerie atmosphere, mysterious, cinematic, ultra-realistic, 4k"
                },
                {
                    "number": 4,
                    "title": "騒音地獄",
                    "description": "24時間大音量の音楽が流れる",
                    "video_prompt": "A room with massive speakers, sound waves visible, vibrating walls, intense noise, chaotic energy, cinematic, ultra-realistic, 4k"
                }
            ]
        }
    
    def validate_content(self, question_data: Dict) -> bool:
        """
        生成されたコンテンツが適切かチェック
        
        Args:
            question_data: 質問データ
            
        Returns:
            適切な場合True
        """
        # 必須フィールドチェック
        required_fields = ["question", "choices"]
        if not all(field in question_data for field in required_fields):
            return False
        
        # 選択肢が4つあるかチェック
        if len(question_data["choices"]) != 4:
            return False
        
        # 各選択肢の必須フィールドチェック
        for choice in question_data["choices"]:
            required_choice_fields = ["number", "title", "description", "video_prompt"]
            if not all(field in choice for field in required_choice_fields):
                return False
        
        return True


if __name__ == "__main__":
    # テスト実行
    import sys
    
    generator = QuestionGenerator()
    
    # カテゴリ指定がある場合
    category = sys.argv[1] if len(sys.argv) > 1 else None
    
    print(f"カテゴリ: {category if category else 'ランダム'}")
    print("\n質問を生成中...")
    
    question_data = generator.generate_question(category)
    
    print("\n=== 生成された質問 ===")
    print(json.dumps(question_data, ensure_ascii=False, indent=2))
    
    # バリデーション
    is_valid = generator.validate_content(question_data)
    print(f"\n✅ バリデーション: {'成功' if is_valid else '失敗'}")
