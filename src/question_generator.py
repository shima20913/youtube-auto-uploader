"""
選択式質問生成モジュール
Gemini APIを使用して視聴者参加型の選択式質問を生成
"""

import json
import random
import os
from datetime import datetime
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

        # カテゴリの重み付け（大金獲得チャレンジを多めに）
        self.category_weights = {
            "大金獲得チャレンジ": 4,
            "究極の選択": 2,
            "好みタイプ診断": 2,
            "恋愛・人間関係": 2,
        }

        # 履歴ファイルのパス
        self.history_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "output", "question_history.json"
        )
        self.history_max = 30  # 直近30件を記憶

        
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
1. 質問文: キャッチーで興味を引く質問（例: 「1週間耐えたら5億円！どの部屋を選ぶ？」）。**30文字以内**で短くまとめること
2. 補足条件: 1つの短い注意事項（例: 「※1週間外出禁止です！」）
3. 選択肢: 4つの異なる環境や条件を提示
4. 各選択肢の特徴:
   - どれも選びにくいが、完全に不可能ではない
   - 過酷さの「種類」を多様にする。以下のどれかを組み合わせること：
     ・物理的つらさ（暑い・寒い・臭い・うるさいなど）
     ・精神的つらさ（孤独・恥ずかしい・退屈など）
     ・シュール・ユーモア系（おっさんだらけ・力士だらけ・腐った飯だらけなど）
     ・誘惑あり但し罠あり（美女だらけだが会話禁止、など）
   - 4つ全部を「物理的苦痛」だけにするのは禁止。バラエティを持たせること
   - 視聴者が思わず笑ってしまうシュールな選択肢を1〜2個入れると良い
5. YouTube規約準拠: 暴力的、性的、差別的な内容は一切含めない

【良い例（雰囲気の参考。これらと同じ設定は使わないこと）】
- 「1週間過ごしたら1億円！どの部屋を選ぶ？」→ おっさんだらけ / 美女だらけだが会話禁止 / 腐った飯しかない / 力士だらけ
- 「24時間一緒にいたら5億円！相手は誰？」→ 爆笑芸人 / 無口な天才 / うるさいおばちゃん / 赤ちゃん10人
- 「1ヶ月住んだら3億円！どこを選ぶ？」→ 時速300kmの新幹線の中 / 人気アイドルのファンクラブ本部 / 野生のサルの群れの中 / 24時間営業のカラオケ

【出力形式】
以下のJSON形式で出力してください：
{
  "question": "キャッチーな質問文",
  "context": "補足条件（※付き）",
  "reward": "報酬額",
  "choices": [
    {
      "number": 1,
      "title": "選択肢のタイトル（8文字以内）",
      "description": "詳細説明（15文字程度）",
      "video_prompt": "Sora 2 AI動画生成用の英語プロンプト。【重要】1つのシーン・1つの動作のみを描写すること。'then'/'contrasted with'/'juxtaposed with' などで複数シーンを繋げるのは禁止。その選択肢の最もインパクトある瞬間を5〜10秒の映像として表現。例: 'A person sleeping soundly in a cozy bed, soft morning light, peaceful expression, cinematic, 4K'"
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
「どれを選んでも後悔しそう」な究極のジレンマ

【要件】
1. 質問文: 思わず「え、どうしよう」と悩んでしまうキャッチーな問い（例：「一生このどちらかしか食べられないとしたら？」）。**30文字以内**で短くまとめること
2. 補足条件: 選択を不可逆にする1文（例：「※一度選んだら一生変更できません」）
3. 選択肢: 4つ。どれを選んでも何かを失うような葛藤がある
4. 各選択肢の特徴:
   - 明確なメリットと、それと同等のデメリットがある
   - 「これを失うのは無理…」と視聴者が感じるものを各選択肢に仕込む
   - 日常ネタ・食べ物・お金・人間関係・能力など、軸を毎回変えること
   - 無難で葛藤のない選択肢は禁止（「どれでもいい」と思えるものはNG）
   - コメント欄で「俺は〇〇！」と言いたくなる個性を持たせる
5. YouTube規約準拠: 暴力的、性的、差別的な内容は一切含めない

【良い例（雰囲気の参考。これらと同じ設定は使わないこと）】
- 「一生このどちらかしか使えないとしたら？※今すぐ決めてください」
  → スマホのみ（PCなし）/ PCのみ（スマホなし）/ 現金のみ（カードなし）/ カードのみ（現金なし）
- 「あなたの人生から1つだけ永久に消えるとしたら？※拒否権なし」
  → 音楽 / 睡眠中の夢 / 甘いもの / 休日

【出力形式】
以下のJSON形式で出力してください：
{
  "question": "質問文",
  "context": "補足条件（※付き）",
  "choices": [
    {
      "number": 1,
      "title": "選択肢タイトル（8文字以内）",
      "description": "詳細説明（失うものや制約を含む、20文字程度）",
      "video_prompt": "Sora 2 AI動画生成用の英語プロンプト。【重要】1つのシーン・1つの動作のみを描写すること。'then'/'contrasted with'/'juxtaposed with' などで複数シーンを繋げるのは禁止。その選択肢の核心的な映像を5〜10秒で表現。例: 'A wealthy person counting large stacks of cash alone in an empty penthouse, cold lighting, cinematic, 4K'"
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
非日常・ファンタジー・シュールな世界観で、選んだ選択肢から隠れた性格や運命が明かされる診断

【世界観のバリエーション（毎回どれかをランダムに使うこと）】
- ファンタジー系：異世界転生・魔法・神様との契約・前世・呪い・奇跡
- SF・未来系：宇宙人と遭遇・タイムスリップ・AIに支配された世界
- シュール・ユーモア系：なぜかその状況に置かれている・不思議な設定（例：「突然動物になるとしたら？」「家の中に謎の扉があったら？」）

【要件】
1. 質問文: 非日常・ファンタジー・シュールを前提にした、想像力を刺激するキャッチーな問い。**30文字以内**で短くまとめること
2. 補足条件: 世界観を補強する1文（例：「※一度選んだら変更できません」「※どれか1つだけ与えられます」）
3. 選択肢: 4つ。それぞれ全く異なる世界観・能力・運命・キャラクター
4. 各選択肢の特徴:
   - どれも魅力的か個性的で、1つしか選べない切実さや面白さがある
   - 「代償」や「制約」「意外な落とし穴」があるとさらに良い
   - 視聴者が「自分ならこれ！」と即座に反応できる個性
   - 日常的・無難な選択肢は禁止（「旅行」「読書」「友達と遊ぶ」などはNG）
5. YouTube規約準拠: 暴力的、性的、差別的な内容は一切含めない

【良い例（雰囲気の参考。これらと同じ設定は使わないこと）】
- 「神様から1つだけ能力をもらえるとしたら？※その能力と引き換えに1つを失います」
  → 時間を止める力（代償：感情を失う）/ 何でも治せる力（代償：自分は治せない）
- 「突然動物に変身するとしたら？※変身を完全には制御できません」
  → 鷹（空を飛べるが人語を忘れる）/ 猫（のんびりできるが好奇心が止まらない）
- 「異世界に転生するとしたら、あなたの職業は？※元の記憶は消えます」
  → 勇者（強いが常に命がけ）/ 魔王（強大な力があるが孤独）

【出力形式】
以下のJSON形式で出力してください：
{
  "question": "質問文",
  "context": "補足条件",
  "choices": [
    {
      "number": 1,
      "title": "選択肢タイトル（8文字以内）",
      "description": "詳細説明（代償や特徴を含む、20文字程度）",
      "video_prompt": "Sora 2 AI動画生成用の英語プロンプト。【重要】1つのシーン・1つの動作のみを描写すること。'then'/'contrasted with'/'juxtaposed with' などで複数シーンを繋げるのは禁止。その選択肢の世界観を5〜10秒の幻想的・映画的映像として表現。例: 'A mage casting a powerful spell in a dark forest, glowing magical energy, dramatic lighting, cinematic, 4K'"
    },
    ... 4つの選択肢
  ]
}

JSON形式のみを出力してください。
"""
            },
            {
                "name": "恋愛・人間関係",
                "prompt_template": """
あなたは視聴者参加型のYouTubeショート動画のシナリオライターです。
以下の条件で、選択式質問を生成してください。

【テーマ】
恋愛・友情・人間関係における「あるある」や「もしも」のジレンマ

【要件】
1. 質問文: 思わず「わかる！」または「え、それどうする？」と反応してしまう問い。**30文字以内**で短くまとめること
2. 補足条件: 状況をリアルに限定する1文（例：「※断れない状況です」「※相手はあなたの本音を知りません」）
3. 選択肢: 4つ。それぞれ異なる人間関係・感情の動きを描く
4. 各選択肢の特徴:
   - リアルな人間の感情や葛藤が透けて見える
   - 「自分もこういう人いる！」と共感できるキャラクターや状況
   - 選択肢ごとに性格の違いが出るようにする。以下の4タイプを必ず1つずつ含めること：
     ・正直・誠実タイプ（建前なしに本音を伝える）
     ・空気読む・波風立てないタイプ（その場をやり過ごす）
     ・ちょっとズルい・逃げるタイプ（既読無視・フェードアウト・嘘をつくなど）
     ・過激・突き抜けるタイプ（思い切った行動・ぶっちゃけすぎ・全力で暴走）
   - 4つのうち少なくとも1つは「正しくはないけどリアルにやりそう」な選択肢にすること
   - 性的・差別的な表現は一切含めない
5. YouTube規約準拠: 暴力的、性的、差別的な内容は一切含めない

【良い例（雰囲気の参考。これらと同じ設定は使わないこと）】
- 「好きな人から告白されたけど、タイミングが最悪。あなたはどうする？※相手は真剣です」
  → 正直に気持ちを伝えて待ってもらう / とりあえず付き合ってみる / やんわり断る / 全力で逃げる
- 「友達のSNSの投稿、どう見ても自慢なんだけど…あなたの反応は？」
  → 素直に「いいね」する / スルーする / 本音でコメントする / そっとミュートする

【出力形式】
以下のJSON形式で出力してください：
{
  "question": "質問文",
  "context": "補足条件（※付き）",
  "choices": [
    {
      "number": 1,
      "title": "選択肢タイトル（8文字以内）",
      "description": "詳細説明（心情や行動を含む、20文字程度）",
      "video_prompt": "Sora 2 AI動画生成用の英語プロンプト。【重要】1つのシーン・1つの感情的瞬間のみを描写すること。'then'/'contrasted with'/'juxtaposed with' などで複数シーンを繋げるのは禁止。その選択肢の感情や行動を5〜10秒の映像として表現。例: 'A person confessing feelings to someone on a park bench at sunset, nervous but sincere expression, cinematic, 4K'"
    },
    ... 4つの選択肢
  ]
}

JSON形式のみを出力してください。
"""
            }
        ]
    
    def _load_history(self) -> List[str]:
        """過去の質問履歴を読み込む"""
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_history(self, question: str) -> None:
        """質問を履歴に追記する"""
        history = self._load_history()
        history.append(question)
        history = history[-self.history_max:]  # 直近N件だけ保持
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def _build_prompt(self, template: str, history: List[str]) -> str:
        """履歴を避けるよう指示をプロンプトに付加する"""
        if not history:
            return template
        recent = "\n".join(f"- {q}" for q in history[-10:])
        avoidance = f"\n【過去に使用済みのお題（これらと似た内容は避けること）】\n{recent}\n"
        # テンプレートの【出力形式】の直前に挿入
        return template.replace("【出力形式】", avoidance + "【出力形式】", 1)

    def generate_question(self, category: str = None) -> Dict:
        """
        選択式質問を生成

        Args:
            category: カテゴリ名（省略時は重み付きランダム）

        Returns:
            生成された質問データ
        """
        # カテゴリ選択（重み付き）
        if category:
            selected_category = next(
                (c for c in self.categories if c["name"] == category),
                None
            )
            if not selected_category:
                selected_category = self._weighted_random_category()
        else:
            selected_category = self._weighted_random_category()

        # 履歴を読み込んでプロンプトに付加
        history = self._load_history()
        prompt = self._build_prompt(selected_category["prompt_template"], history)

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

            # 履歴に保存
            self._save_history(question_data["question"])

            return question_data

        except Exception as e:
            print(f"エラー: {e}")
            # フォールバック: デフォルト質問を返す
            return self._get_fallback_question()

    def _weighted_random_category(self) -> Dict:
        """重み付きランダムでカテゴリを選択"""
        names = [c["name"] for c in self.categories]
        weights = [self.category_weights.get(name, 1) for name in names]
        return random.choices(self.categories, weights=weights, k=1)[0]
    
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
