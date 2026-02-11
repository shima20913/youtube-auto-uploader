"""
ローカル動画生成スクリプト
質問生成 → AI動画生成 → Remotionレンダリング → (YouTube投稿)
"""

import os
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from question_generator import QuestionGenerator
from quiz_video_renderer import QuizVideoRenderer


def generate_video(
    category: str = None,
    test_mode: bool = False,
    skip_ai_videos: bool = False
) -> dict:
    """
    動画を生成してオプションでアップロード

    Args:
        category: 質問カテゴリ（省略時はランダム）
        test_mode: Trueの場合アップロードをスキップ
        skip_ai_videos: TrueのときAI動画生成をスキップ（プレースホルダー使用）

    Returns:
        結果の辞書
    """
    print(f"\n{'='*60}")
    print("YouTube動画自動生成システム (Remotion)")
    print(f"開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    project_root = Path(__file__).parent
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    # ── ステップ 1: 質問生成 ─────────────────────────────────
    print("📝 ステップ 1/3: 質問生成中...")
    generator = QuestionGenerator()
    question_data = generator.generate_question(category)

    print(f"  カテゴリ: {question_data.get('category')}")
    print(f"  質問: {question_data.get('question')}")

    if not generator.validate_content(question_data):
        raise ValueError("生成された質問データが不正です")

    # ── ステップ 2: AI動画生成 ────────────────────────────────
    choices = question_data.get("choices", [])
    video_dir = project_root / "remotion" / "public" / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)

    if skip_ai_videos:
        print("\n⏭️  ステップ 2/3: AI動画生成をスキップ（プレースホルダー使用）")
        for choice in choices:
            choice["videoPath"] = f"videos/placeholder_{choice['number']}.mp4"
    else:
        print("\n🎬 ステップ 2/3: AI動画生成中...")
        try:
            from ai_video_generator import AIVideoGenerator
            ai_gen = AIVideoGenerator()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = output_dir / "temp" / timestamp
            temp_dir.mkdir(parents=True, exist_ok=True)

            prompts = [c["video_prompt"] for c in choices]
            results = ai_gen.generate_multiple_videos(
                prompts=prompts,
                output_dir=str(temp_dir),
                duration=8
            )

            for choice in choices:
                n = choice["number"]
                src_path = results.get(n)
                if src_path and os.path.exists(src_path):
                    dest = video_dir / f"choice_{n}.mp4"
                    shutil.copy2(src_path, dest)
                    choice["videoPath"] = f"videos/choice_{n}.mp4"
                    print(f"  ✅ 選択肢{n}: {dest.name}")
                else:
                    choice["videoPath"] = f"videos/placeholder_{n}.mp4"
                    print(f"  ⚠️  選択肢{n}: 生成失敗 → プレースホルダー使用")

            # 一時ファイル削除
            shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            print(f"  ❌ AI動画生成エラー: {e}")
            print("  → プレースホルダーで続行します")
            for choice in choices:
                choice["videoPath"] = f"videos/placeholder_{choice['number']}.mp4"

    # ── 英語翻訳 ──────────────────────────────────────────────
    print("\n🌐 英語翻訳中...")
    translations = _translate_to_english(question_data)

    # ── ステップ 3: Remotionレンダリング ──────────────────────
    print("\n🎞️  ステップ 3/3: Remotionレンダリング中...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"quiz_{timestamp}.mp4"

    renderer = QuizVideoRenderer(remotion_dir=str(project_root / "remotion"))

    # Remotion用データ構築
    remotion_choices = [
        {
            "number": c["number"],
            "text": c["title"],
            "textEn": translations["choices"].get(c["number"], c["title"]),
            "videoPath": c["videoPath"],
        }
        for c in choices
    ]

    question_text = question_data.get("question", "")
    end_msg = "あなたはどれを選んだ？\nコメント欄で教えて！"

    success = renderer.render_quiz_video(
        question=question_text,
        question_en=translations["question"],
        choices=remotion_choices,
        end_message=end_msg,
        end_message_en="Which did you choose?\nTell us in the comments!",
        output_path=str(output_path),
    )

    if not success:
        raise RuntimeError("Remotionレンダリングに失敗しました")

    result = {
        "category": question_data.get("category"),
        "question": question_text,
        "video_path": str(output_path),
        "success": True,
    }

    # ── YouTube投稿（test_mode=Falseのとき） ─────────────────
    if not test_mode:
        print("\n📤 YouTube投稿中...")
        try:
            from youtube_uploader import YouTubeUploader
            from discord_notifier import DiscordNotifier

            uploader = YouTubeUploader()
            description = _build_description(question_data)
            upload_result = uploader.upload_short(
                video_path=str(output_path),
                title=question_text,
                description=description,
                hashtags="#Shorts #質問 #選択式 #あなたはどっち",
            )
            result["video_url"] = upload_result["video_url"]
            result["video_id"] = upload_result["video_id"]

            notifier = DiscordNotifier()
            notifier.notify_upload_success(
                video_url=upload_result["video_url"],
                title=question_text,
                genre=question_data.get("category", "質問"),
            )
        except Exception as e:
            print(f"  ❌ 投稿エラー: {e}")
            result["upload_error"] = str(e)
    else:
        print("\n⏭️  テストモード: YouTube投稿をスキップ")
        result["video_url"] = "テストモード"

    print(f"\n{'='*60}")
    print(f"✅ 完了!")
    print(f"   動画: {output_path}")
    if not test_mode and "video_url" in result:
        print(f"   URL : {result['video_url']}")
    print(f"{'='*60}\n")

    return result


def _translate_to_english(question_data: dict) -> dict:
    """Geminiで質問と選択肢を英訳する"""
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        load_dotenv()
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("models/gemini-2.5-flash")

        choices_ja = "\n".join(
            f"{c['number']}. {c['title']}" for c in question_data.get("choices", [])
        )
        prompt = f"""Translate the following Japanese quiz content into natural English.
Return JSON only in this format:
{{
  "question": "...",
  "choices": {{
    "1": "...",
    "2": "...",
    "3": "...",
    "4": "..."
  }}
}}

Question: {question_data.get("question", "")}
Choices:
{choices_ja}"""

        response = model.generate_content(prompt)
        content = response.text.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json
        data = json.loads(content.strip())
        # choicesのキーをintに変換
        choices_en = {int(k): v for k, v in data.get("choices", {}).items()}
        print(f"  質問EN: {data.get('question', '')}")
        return {"question": data.get("question", ""), "choices": choices_en}
    except Exception as e:
        print(f"  ⚠️ 翻訳失敗: {e} → 日本語をそのまま使用")
        choices_fallback = {c["number"]: c["title"] for c in question_data.get("choices", [])}
        return {"question": question_data.get("question", ""), "choices": choices_fallback}


def _build_description(question_data: dict) -> str:
    desc = f"{question_data.get('question', '')}\n\n"
    if "context" in question_data:
        desc += f"{question_data['context']}\n\n"
    desc += "【選択肢】\n"
    for c in question_data.get("choices", []):
        desc += f"{'①②③④'[c['number']-1]} {c['title']} - {c.get('description', '')}\n"
    desc += "\n💬 あなたはどれを選びますか？コメント欄で教えてください！\n"
    desc += "👍 面白かったら高評価とチャンネル登録お願いします！\n"
    return desc


def main():
    parser = argparse.ArgumentParser(description="YouTube動画ローカル生成スクリプト")
    parser.add_argument(
        "--category",
        choices=["大金獲得チャレンジ", "究極の選択", "好みタイプ診断", "恋愛・人間関係"],
        default=None,
        help="質問カテゴリ（省略時はランダム）",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="テストモード: YouTube投稿をスキップ",
    )
    parser.add_argument(
        "--skip-videos",
        action="store_true",
        help="AI動画生成をスキップしてプレースホルダーを使用",
    )
    args = parser.parse_args()

    result = generate_video(
        category=args.category,
        test_mode=args.test,
        skip_ai_videos=args.skip_videos,
    )

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
