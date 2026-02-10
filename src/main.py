"""
メインスクリプト（選択式質問動画用）
質問生成から動画作成、投稿までの全プロセスを統合
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

from question_generator import QuestionGenerator
from ai_video_generator import AIVideoGenerator
from video_creator import QuestionVideoCreator
from youtube_uploader import YouTubeUploader
from discord_notifier import DiscordNotifier


class QuestionVideoAutoUploader:
    """選択式質問動画自動投稿システム"""
    
    def __init__(self):
        """初期化"""
        self.question_generator = QuestionGenerator()
        self.ai_video_generator = AIVideoGenerator()
        self.video_creator = QuestionVideoCreator()
        self.youtube_uploader = None
        self.discord_notifier = None
        
        # 出力ディレクトリ
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # 一時ディレクトリ（AI生成動画用）
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
    
    def generate_and_upload(self, category: str = None, test_mode: bool = False) -> dict:
        """
        動画を生成してアップロード
        
        Args:
            category: 質問カテゴリ（省略時はランダム）
            test_mode: テストモード (アップロードをスキップ)
            
        Returns:
            結果の辞書
        """
        try:
            print(f"\n{'='*70}")
            print(f"選択式質問動画自動生成システム")
            print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}\n")
            
            # 1. 質問生成
            print("📝 ステップ 1/5: 質問生成中...")
            question_data = self.question_generator.generate_question(category)
            
            print(f"カテゴリ: {question_data.get('category')}")
            print(f"質問: {question_data.get('question')}")
            print(f"選択肢数: {len(question_data.get('choices', []))}")
            
            # バリデーション
            if not self.question_generator.validate_content(question_data):
                raise ValueError("生成された質問データが不正です")
            
            # 2. AI動画生成（4つの選択肢を並列生成）
            print("\n🎬 ステップ 2/5: AI動画生成中...")
            print("（4つの選択肢動画を並列生成します。数分かかる場合があります）\n")
            
            # タイムスタンプで一時ディレクトリを作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_temp_dir = self.temp_dir / timestamp
            session_temp_dir.mkdir(exist_ok=True)
            
            # プロンプトリストを作成
            prompts = [
                choice['video_prompt'] 
                for choice in question_data['choices']
            ]
            
            # 並列生成
            choice_videos = self.ai_video_generator.generate_multiple_videos(
                prompts=prompts,
                output_dir=str(session_temp_dir),
                duration=8
            )
            
            # 生成に成功した動画数を確認
            success_count = sum(1 for v in choice_videos.values() if v is not None)
            print(f"\n✅ {success_count}/4 本の選択肢動画を生成しました")
            
            if success_count < 4:
                print("⚠️  一部の動画生成に失敗しました。フォールバック処理を行います。")
            
            # 3. 最終動画作成
            print("\n🎞️  ステップ 3/5: 最終動画作成中...")
            final_video_path = self.output_dir / f"question_{timestamp}.mp4"
            
            self.video_creator.create_question_video(
                question_data=question_data,
                choice_videos=choice_videos,
                output_path=str(final_video_path)
            )
            
            # 4. YouTubeメタデータ準備
            title = question_data.get('question', '選択式質問')
            description = self._create_description(question_data)
            hashtags = "#Shorts #質問 #選択式 #あなたはどっち"
            
            result = {
                'category': question_data.get('category'),
                'question': question_data.get('question'),
                'video_path': str(final_video_path),
                'success': True
            }
            
            # 5. YouTube投稿
            if not test_mode:
                print("\n📤 ステップ 4/5: YouTube投稿中...")
                
                if self.youtube_uploader is None:
                    self.youtube_uploader = YouTubeUploader()
                
                upload_result = self.youtube_uploader.upload_short(
                    video_path=str(final_video_path),
                    title=title,
                    description=description,
                    hashtags=hashtags
                )
                
                result['video_url'] = upload_result['video_url']
                result['video_id'] = upload_result['video_id']
                
                # Discord通知
                print("\n📢 ステップ 5/5: Discord通知送信中...")
                if self.discord_notifier is None:
                    self.discord_notifier = DiscordNotifier()
                
                self.discord_notifier.notify_upload_success(
                    video_url=upload_result['video_url'],
                    title=title,
                    genre=question_data.get('category', '質問')
                )
            else:
                print("\n⏭️  ステップ 4-5/5: テストモードのため投稿をスキップ")
                result['video_url'] = "テストモード"
            
            # クリーンアップ（オプション）
            if not test_mode:
                print("\n🧹 一時ファイルをクリーンアップ中...")
                self._cleanup_temp_files(session_temp_dir)
            
            print(f"\n{'='*70}")
            print(f"✅ 完了!")
            print(f"動画パス: {final_video_path}")
            if not test_mode:
                print(f"YouTube URL: {result['video_url']}")
            print(f"{'='*70}\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            
            # エラー通知
            if not test_mode and self.discord_notifier:
                self.discord_notifier.notify_error(
                    error_message=str(e),
                    genre=category or "質問動画"
                )
            
            return {
                'category': category,
                'success': False,
                'error': str(e)
            }
    
    def _create_description(self, question_data: Dict) -> str:
        """
        YouTube用の説明文を生成
        
        Args:
            question_data: 質問データ
            
        Returns:
            説明文
        """
        description = f"{question_data.get('question')}\n\n"
        
        if 'context' in question_data:
            description += f"{question_data['context']}\n\n"
        
        description += "【選択肢】\n"
        for choice in question_data.get('choices', []):
            description += f"❶{choice['number']}. {choice['title']} - {choice.get('description', '')}\n"
        
        description += "\n💬 あなたはどれを選びますか？コメント欄で教えてください！\n"
        description += "\n👍 面白かったら高評価とチャンネル登録お願いします！\n"
        
        return description
    
    def _cleanup_temp_files(self, temp_dir: Path):
        """一時ファイルを削除"""
        try:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                print(f"✅ 一時ファイルを削除しました: {temp_dir}")
        except Exception as e:
            print(f"⚠️  一時ファイル削除エラー: {e}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='選択式質問動画自動生成・投稿システム'
    )
    parser.add_argument(
        '--category',
        type=str,
        choices=['大金獲得チャレンジ', '究極の選択', '好みタイプ診断'],
        default=None,
        help='質問のカテゴリ（省略時はランダム）'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='テストモード (アップロードをスキップ)'
    )
    
    args = parser.parse_args()
    
    # システムを実行
    uploader = QuestionVideoAutoUploader()
    result = uploader.generate_and_upload(
        category=args.category,
        test_mode=args.test
    )
    
    # 結果を出力
    if result['success']:
        print("✅ すべての処理が正常に完了しました!")
        sys.exit(0)
    else:
        print("❌ 処理中にエラーが発生しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
