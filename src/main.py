"""
メインスクリプト
動画生成から投稿までの全プロセスを統合
"""

import os
import sys
import argparse
import random
from datetime import datetime
from pathlib import Path

from content_generator import get_generator
from tts_engine import TTSEngine
from asset_manager import AssetManager
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader
from discord_notifier import DiscordNotifier


class YouTubeAutoUploader:
    """YouTube自動投稿システム"""
    
    def __init__(self):
        """初期化"""
        self.content_generator = None
        self.tts_engine = TTSEngine()
        self.asset_manager = AssetManager()
        self.video_creator = VideoCreator()
        self.youtube_uploader = None
        self.discord_notifier = None
        
        # 出力ディレクトリ
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_and_upload(self, genre: str, test_mode: bool = False) -> dict:
        """
        動画を生成してアップロード
        
        Args:
            genre: ジャンル (horror, trivia, satisfying)
            test_mode: テストモード (アップロードをスキップ)
            
        Returns:
            結果の辞書
        """
        try:
            print(f"\n{'='*60}")
            print(f"ジャンル: {genre}")
            print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")
            
            # 1. コンテンツ生成
            print("📝 ステップ 1/5: スクリプト生成中...")
            generator = get_generator(genre)
            content = generator.generate_content()
            
            print(f"タイトル: {content['title']}")
            print(f"スクリプト長: {len(content['script'])}文字")
            
            # 2. 音声合成
            print("\n🎤 ステップ 2/5: 音声合成中...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = self.output_dir / f"{genre}_{timestamp}_audio.mp3"
            
            self.tts_engine.generate_for_genre(
                text=content['script'],
                genre=genre,
                output_path=str(audio_path)
            )
            
            # 3. 素材取得
            print("\n🎨 ステップ 3/5: 背景素材取得中...")
            try:
                background_path = self.asset_manager.get_image_for_genre(
                    keywords=content['keywords'],
                    genre=genre
                )
            except Exception as e:
                print(f"素材取得エラー: {e}")
                print("デフォルト素材を使用します")
                # フォールバック: 単色背景を生成
                background_path = self._create_default_background(genre)
            
            # 4. 動画生成
            print("\n🎬 ステップ 4/5: 動画生成中...")
            video_path = self.output_dir / f"{genre}_{timestamp}_video.mp4"
            
            self.video_creator.create_video(
                background_path=background_path,
                audio_path=str(audio_path),
                script=content['script'],
                output_path=str(video_path),
                genre=genre
            )
            
            result = {
                'genre': genre,
                'title': content['title'],
                'video_path': str(video_path),
                'success': True
            }
            
            # 5. YouTube投稿
            if not test_mode:
                print("\n📤 ステップ 5/5: YouTube投稿中...")
                
                if self.youtube_uploader is None:
                    self.youtube_uploader = YouTubeUploader()
                
                upload_result = self.youtube_uploader.upload_short(
                    video_path=str(video_path),
                    title=content['title'],
                    description=content['description'],
                    hashtags=content['hashtags']
                )
                
                result['video_url'] = upload_result['video_url']
                result['video_id'] = upload_result['video_id']
                
                # Discord通知
                print("\n📢 Discord通知送信中...")
                if self.discord_notifier is None:
                    self.discord_notifier = DiscordNotifier()
                
                self.discord_notifier.notify_upload_success(
                    video_url=upload_result['video_url'],
                    title=content['title'],
                    genre=genre
                )
            else:
                print("\n⏭️  ステップ 5/5: テストモードのため投稿をスキップ")
                result['video_url'] = "テストモード"
            
            print(f"\n✅ 完了!")
            print(f"動画パス: {video_path}")
            if not test_mode:
                print(f"YouTube URL: {result['video_url']}")
            
            return result
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            
            # エラー通知
            if not test_mode and self.discord_notifier:
                self.discord_notifier.notify_error(
                    error_message=str(e),
                    genre=genre
                )
            
            return {
                'genre': genre,
                'success': False,
                'error': str(e)
            }
    
    def _create_default_background(self, genre: str) -> str:
        """
        デフォルトの単色背景を生成
        
        Args:
            genre: ジャンル
            
        Returns:
            背景画像のパス
        """
        from PIL import Image
        
        # ジャンル別の色
        colors = {
            'horror': (20, 20, 30),      # ダークブルー
            'trivia': (30, 50, 80),      # ネイビー
            'satisfying': (80, 30, 50)   # ダークピンク
        }
        
        color = colors.get(genre, (30, 30, 30))
        
        # 1080x1920の画像を生成
        img = Image.new('RGB', (1080, 1920), color)
        
        output_path = self.output_dir / f"default_bg_{genre}.png"
        img.save(output_path)
        
        return str(output_path)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='YouTube自動投稿システム'
    )
    parser.add_argument(
        '--genre',
        type=str,
        choices=['horror', 'trivia', 'satisfying', 'random'],
        default='random',
        help='動画のジャンル'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='テストモード (アップロードをスキップ)'
    )
    
    args = parser.parse_args()
    
    # ジャンルをランダム選択
    if args.genre == 'random':
        genre = random.choice(['horror', 'trivia', 'satisfying'])
        print(f"ランダムに選択されたジャンル: {genre}")
    else:
        genre = args.genre
    
    # システムを実行
    uploader = YouTubeAutoUploader()
    result = uploader.generate_and_upload(genre, test_mode=args.test)
    
    # 結果を出力
    if result['success']:
        print("\n" + "="*60)
        print("✅ すべての処理が正常に完了しました!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ 処理中にエラーが発生しました")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
