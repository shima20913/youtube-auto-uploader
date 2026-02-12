"""
Discord Bot モジュール - シンプル版
お題投稿、動画収集、自動処理を行うBot
"""

import os
import discord
from discord.ext import tasks
from datetime import time, datetime
import pytz
import json
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

# グローバルクライアント
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

# 設定
QUESTION_CHANNEL_ID = int(os.getenv("DISCORD_QUESTION_CHANNEL_ID", 0))
TIMEZONE = pytz.timezone('Asia/Tokyo')

# データディレクトリ
DATA_DIR = Path("output/discord_data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_DIR = Path("output/discord_videos")
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

# アクティブなお題
active_questions: Dict[int, Dict] = {}

# モジュール（遅延初期化）
question_generator = None
youtube_uploader = None
discord_notifier = None


@client.event
async def on_ready():
    """Bot起動時"""
    print(f'✅ Discord Bot起動: {client.user.name}')
    print(f'チャンネルID: {QUESTION_CHANNEL_ID}')
    print(f'使用可能なコマンド: !ping, !test, !status, !reset')
    
    # データ復元
    load_active_questions()
    
    # 定期タスク開始
    if not post_daily_question.is_running():
        post_daily_question.start()


@client.event
async def on_message(message):
    """メッセージ受信時"""
    # Bot自身は無視
    if message.author.bot:
        return
    
    # コマンド処理
    if message.content.startswith('!'):
        await handle_command(message)
    
    # スレッド内の動画処理
    if isinstance(message.channel, discord.Thread):
        await handle_thread_message(message)


async def handle_command(message):
    """コマンド処理"""
    content = message.content[1:].strip()  # ! を除去
    
    if content == 'ping':
        await message.channel.send(f"🏓 Pong! レイテンシ: {round(client.latency * 1000)}ms")
    
    elif content == 'test':
        await message.channel.send("📝 テスト用お題を投稿します...")
        try:
            await post_question()
            await message.channel.send("✅ お題投稿完了！")
        except Exception as e:
            await message.channel.send(f"❌ エラー: {str(e)}")
            import traceback
            traceback.print_exc()
    
    elif content == 'status':
        if isinstance(message.channel, discord.Thread):
            thread_id = message.channel.id
            if thread_id in active_questions:
                info = active_questions[thread_id]
                await message.channel.send(
                    f"**進捗:** {len(info['videos'])}/4本\n"
                    f"**お題:** {info['question_data']['question']}"
                )
            else:
                await message.channel.send("⚠️ このスレッドはアクティブなお題ではありません。")
        else:
            await message.channel.send(f"📊 アクティブなお題: {len(active_questions)}件")
    
    elif content == 'reset':
        if isinstance(message.channel, discord.Thread):
            thread_id = message.channel.id
            if thread_id in active_questions:
                del active_questions[thread_id]
                save_active_questions()
                await message.channel.send("✅ このスレッドをリセットしました。")
            else:
                await message.channel.send("⚠️ このスレッドはアクティブなお題ではありません。")
        else:
            await message.channel.send("⚠️ このコマンドはスレッド内でのみ使用できます。")


@tasks.loop(time=time(hour=19, minute=0, tzinfo=TIMEZONE))
async def post_daily_question():
    """毎日19時にお題投稿"""
    try:
        print(f"\n{'='*60}")
        print(f"[{datetime.now(TIMEZONE)}] 定期お題投稿開始")
        print(f"{'='*60}\n")
        
        await post_question()
        
    except Exception as e:
        print(f"❌ お題投稿エラー: {e}")
        import traceback
        traceback.print_exc()


async def post_question():
    """お題を生成してDiscordに投稿"""
    global question_generator

    # モジュール初期化
    if question_generator is None:
        from question_generator import QuestionGenerator
        question_generator = QuestionGenerator()
    
    # チャンネル取得
    channel = client.get_channel(QUESTION_CHANNEL_ID)
    if not channel:
        print(f"❌ チャンネルが見つかりません: {QUESTION_CHANNEL_ID}")
        return
    
    # 質問生成
    print("📝 質問生成中...")
    question_data = question_generator.generate_question()
    
    # Embed作成
    embed = create_question_embed(question_data)
    
    # メッセージ投稿
    message = await channel.send(embed=embed)
    
    # スレッド作成
    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    thread = await message.create_thread(
        name=f"📹 {today} のお題 - 動画投稿用",
        auto_archive_duration=1440
    )
    
    # 説明投稿
    instructions = "Sora 2で以下のプロンプトで動画を生成して、順番に投稿してください（**選択肢1→2→3→4**）\n4本揃ったら自動でYouTube投稿します！"
    await thread.send(instructions)

    # 各選択肢のプロンプトを個別メッセージで送信（スマホでコピーしやすくする）
    circled = ['①', '②', '③', '④']
    for choice in question_data.get('choices', []):
        n = choice['number']
        prompt = choice.get('video_prompt', '')
        await thread.send(
            f"**{circled[n-1]} {choice['title']}**\n```\n{prompt}\n```"
        )
    
    # データ保存
    question_id = f"{today}_{message.id}"
    active_questions[thread.id] = {
        "id": question_id,
        "question_data": question_data,
        "thread_id": thread.id,
        "message_id": message.id,
        "videos": {},
        "created_at": datetime.now(TIMEZONE).isoformat()
    }
    
    save_active_questions()
    
    print(f"✅ お題を投稿しました: {question_data['question']}")
    print(f"スレッドID: {thread.id}")


def create_question_embed(question_data: Dict) -> discord.Embed:
    """質問用Embed作成"""
    embed = discord.Embed(
        title="🎬 今日のお題",
        description=f"**{question_data['question']}**\n{question_data.get('context', '')}",
        color=0xFFD700
    )
    
    for choice in question_data['choices']:
        prompt = choice['video_prompt']
        if len(prompt) > 300:
            prompt = prompt[:297] + "..."
        
        embed.add_field(
            name=f"❶{choice['number']}. {choice['title']}",
            value=f"*{choice.get('description', '')}*\n\n**Sora 2 Prompt:**\n```\n{prompt}\n```",
            inline=False
        )
    
    embed.set_footer(text="スレッドに動画を投稿してください")
    embed.timestamp = datetime.now(TIMEZONE)
    
    return embed


async def handle_thread_message(message):
    """スレッド内のメッセージ処理"""
    thread_id = message.channel.id
    
    if thread_id not in active_questions:
        return
    
    question_info = active_questions[thread_id]
    
    # 動画添付確認
    videos = [a for a in message.attachments 
              if a.content_type and a.content_type.startswith('video/')]
    
    if not videos:
        return
    
    # 動画保存
    for video in videos:
        current_count = len(question_info['videos'])
        
        if current_count >= 4:
            await message.channel.send("⚠️ すでに4本の動画が揃っています。")
            break
        
        choice_number = current_count + 1
        
        # 保存
        video_path = VIDEO_DIR / question_info['id'] / f"choice_{choice_number}.mp4"
        video_path.parent.mkdir(parents=True, exist_ok=True)
        
        await video.save(video_path)
        
        question_info['videos'][choice_number] = str(video_path)
        
        # 確認
        await message.add_reaction('✅')
        await message.channel.send(
            f"✅ **選択肢{choice_number}** として受け付けました！ "
            f"(**{len(question_info['videos'])}/4本**)"
        )
    
    save_active_questions()
    
    # 4本揃ったか確認
    if len(question_info['videos']) == 4:
        await finalize_question(thread_id)


async def finalize_question(thread_id: int):
    """4本揃ったら最終処理"""
    global youtube_uploader, discord_notifier

    question_info = active_questions[thread_id]
    thread = client.get_channel(thread_id)
    question_data = question_info['question_data']

    await thread.send("🎬 **4本揃いました！YouTube投稿処理を開始します...**")

    try:
        # モジュール初期化
        if youtube_uploader is None:
            from youtube_uploader import YouTubeUploader
            youtube_uploader = YouTubeUploader()

        if discord_notifier is None:
            from discord_notifier import DiscordNotifier
            discord_notifier = DiscordNotifier()

        # 1. 動画をRemotion publicディレクトリにコピー
        await thread.send("📹 動画をレンダリング中（Remotion）...")

        import shutil
        project_root = Path(__file__).parent.parent
        remotion_video_dir = project_root / "remotion" / "public" / "videos"
        remotion_video_dir.mkdir(parents=True, exist_ok=True)

        choices = question_data.get('choices', [])
        remotion_choices = []
        for choice in choices:
            n = choice['number']
            src = question_info['videos'].get(n)
            if src and Path(src).exists():
                dest = remotion_video_dir / f"discord_{question_info['id']}_choice_{n}.mp4"
                shutil.copy2(src, dest)
                video_path = f"videos/{dest.name}"
            else:
                video_path = f"videos/placeholder_{n}.mp4"
            remotion_choices.append({
                "number": n,
                "text": choice['title'],
                "textEn": choice['title'],  # 翻訳は後で上書き
                "videoPath": video_path,
            })

        # 2. Gemini英訳
        translations = _translate_to_english_sync(question_data)
        for rc in remotion_choices:
            rc['textEn'] = translations['choices'].get(rc['number'], rc['text'])

        # 3. Remotionレンダリング
        from quiz_video_renderer import QuizVideoRenderer
        output_dir = project_root / "output"
        output_dir.mkdir(exist_ok=True)
        final_video_path = VIDEO_DIR / question_info['id'] / "final.mp4"
        final_video_path.parent.mkdir(parents=True, exist_ok=True)

        renderer = QuizVideoRenderer(remotion_dir=str(project_root / "remotion"))
        success = renderer.render_quiz_video(
            question=question_data.get('question', ''),
            question_en=translations['question'],
            choices=remotion_choices,
            end_message="あなたはどれを選んだ？\nコメント欄で教えて！",
            end_message_en="Which did you choose?\nTell us in the comments!",
            output_path=str(final_video_path),
        )

        # コピーしたRemotion用動画をクリーンアップ
        for rc in remotion_choices:
            p = remotion_video_dir / Path(rc['videoPath']).name
            if p.exists() and p.name.startswith('discord_'):
                p.unlink()

        if not success:
            raise RuntimeError("Remotionレンダリングに失敗しました")

        # 4. YouTube投稿
        await thread.send("📤 YouTubeに投稿中...")
        
        title = question_info['question_data']['question']
        description = create_youtube_description(question_info['question_data'])
        
        upload_result = youtube_uploader.upload_short(
            video_path=str(final_video_path),
            title=title,
            description=description,
            hashtags="#Shorts #質問 #選択式 #あなたはどっち"
        )
        
        # 3. 完了通知
        video_url = upload_result['video_url']
        
        success_embed = discord.Embed(
            title="✅ YouTube投稿完了！",
            description=f"**{title}**",
            color=0x00FF00,
            url=video_url
        )
        success_embed.add_field(name="🔗 動画URL", value=video_url, inline=False)
        
        await thread.send(embed=success_embed)
        
        # Webhook通知
        discord_notifier.notify_upload_success(
            video_url=video_url,
            title=title,
            genre=question_info['question_data'].get('category', '質問')
        )
        
        # クリーンアップ
        del active_questions[thread_id]
        save_active_questions()
        
        print(f"✅ YouTube投稿完了: {video_url}")
        
    except Exception as e:
        await thread.send(f"❌ **エラーが発生しました:**\n```{str(e)}```")
        print(f"❌ 最終処理エラー: {e}")
        import traceback
        traceback.print_exc()


def create_youtube_description(question_data: Dict) -> str:
    """YouTube説明文生成"""
    description = f"{question_data['question']}\n\n"
    
    if 'context' in question_data:
        description += f"{question_data['context']}\n\n"
    
    description += "【選択肢】\n"
    for choice in question_data['choices']:
        description += f"❶{choice['number']}. {choice['title']} - {choice.get('description', '')}\n"
    
    description += "\n💬 あなたはどれを選びますか？コメント欄で教えてください！\n"
    description += "\n👍 面白かったら高評価とチャンネル登録お願いします！\n"
    
    return description


def _translate_to_english_sync(question_data: dict) -> dict:
    """Geminiで質問と選択肢を英訳する（同期版）"""
    try:
        import google.generativeai as genai
        import json as _json
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
        data = _json.loads(content.strip())
        choices_en = {int(k): v for k, v in data.get("choices", {}).items()}
        return {"question": data.get("question", ""), "choices": choices_en}
    except Exception as e:
        print(f"  ⚠️ 翻訳失敗: {e} → 日本語をそのまま使用")
        choices_fallback = {c["number"]: c["title"] for c in question_data.get("choices", [])}
        return {"question": question_data.get("question", ""), "choices": choices_fallback}


def save_active_questions():
    """アクティブなお題を保存"""
    data_file = DATA_DIR / "active_questions.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(active_questions, f, ensure_ascii=False, indent=2)


def load_active_questions():
    """アクティブなお題を復元"""
    global active_questions
    data_file = DATA_DIR / "active_questions.json"
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            active_questions = {int(k): v for k, v in json.load(f).items()}
        print(f"✅ {len(active_questions)}件のアクティブなお題を復元しました")


def main():
    """メイン関数"""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not bot_token:
        print("❌ DISCORD_BOT_TOKEN が設定されていません")
        return
    
    print("🤖 Discord Bot を起動しています...")
    print("Ctrl+C で終了")
    
    client.run(bot_token)


if __name__ == "__main__":
    main()
