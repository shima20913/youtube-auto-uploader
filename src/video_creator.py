"""
動画生成モジュール（選択式質問動画用）
MoviePyを使用して縦型の選択式質問動画を生成
"""

import os
from typing import Dict, List, Optional
from moviepy import (
    VideoFileClip, ImageClip, AudioFileClip,
    TextClip, CompositeVideoClip, concatenate_videoclips,
    ColorClip
)
from moviepy import vfx
import yaml


class QuestionVideoCreator:
    """選択式質問動画生成クラス"""
    
    def __init__(self, config_path: str = "config/video_config.yaml"):
        """
        Args:
            config_path: 設定ファイルのパス
        """
        # 設定ファイルが存在しない場合はデフォルト設定を使用
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._get_default_config()
        
        self.video_config = self.config['video']
        self.width = self.video_config['resolution'][0]
        self.height = self.video_config['resolution'][1]
        self.fps = self.video_config['fps']
        self.durations = self.video_config['duration']
        
        self.text_config = self.config['text_overlay']
        self.audio_config = self.config['audio']
    
    def _get_default_config(self) -> Dict:
        """デフォルト設定を返す"""
        return {
            'video': {
                'resolution': [1080, 1920],  # 縦型
                'fps': 30,
                'duration': {
                    'opening': 6,
                    'choice': 8,
                    'ending': 5
                }
            },
            'text_overlay': {
                'font': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                'colors': {
                    'primary': '#FFFFFF',
                    'accent': '#FFD700',
                    'background': 'rgba(0,0,0,0.7)'
                }
            },
            'audio': {
                'bgm_volume': 0.3,
                'narration_volume': 0.8,
                'sfx_volume': 0.5
            }
        }
    
    def create_question_video(
        self,
        question_data: Dict,
        choice_videos: Dict[int, str],
        output_path: str,
        bgm_path: Optional[str] = None
    ) -> str:
        """
        選択式質問動画を生成
        
        Args:
            question_data: 質問データ
            choice_videos: {選択肢番号: 動画パス} の辞書
            output_path: 出力ファイルパス
            bgm_path: BGMファイルパス（オプション）
            
        Returns:
            生成された動画ファイルのパス
        """
        print("🎬 選択式質問動画を生成中...")
        
        # 出力ディレクトリを作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 各パートを生成
        opening_clip = self._create_opening(question_data)
        choice_clips = self._create_choice_sections(question_data, choice_videos)
        ending_clip = self._create_ending()
        
        # すべてのクリップを結合
        all_clips = [opening_clip] + choice_clips + [ending_clip]
        final_video = concatenate_videoclips(all_clips, method="compose")
        
        # BGMを追加（オプション）
        if bgm_path and os.path.exists(bgm_path):
            bgm = AudioFileClip(bgm_path)
            bgm = bgm.with_effects([vfx.VolumeX(self.audio_config['bgm_volume'])])
            # ループしてビデオの長さに合わせる
            if bgm.duration < final_video.duration:
                n_loops = int(final_video.duration / bgm.duration) + 1
                bgm = concatenate_audioclips([bgm] * n_loops)
            bgm = bgm.subclip(0, final_video.duration)
            
            # 既存の音声とミックス
            if final_video.audio:
                from moviepy import CompositeAudioClip
                final_audio = CompositeAudioClip([final_video.audio, bgm])
                final_video = final_video.with_audio(final_audio)
            else:
                final_video = final_video.with_audio(bgm)
        
        # 動画を書き出し
        print("📹 動画を書き出し中...")
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=4,
            logger=None  # ログを抑制
        )
        
        # クリーンアップ
        final_video.close()
        for clip in all_clips:
            clip.close()
        
        print(f"✅ 動画を生成しました: {output_path}")
        return output_path
    
    def _create_opening(self, question_data: Dict) -> VideoFileClip:
        """オープニングパートを作成"""
        duration = self.durations['opening']
        
        # 背景（黒）
        background = ColorClip(
            size=(self.width, self.height),
            color=(0, 0, 0),
            duration=duration
        )
        
        # 質問文
        question_text = question_data.get('question', '質問')
        context_text = question_data.get('context', '')
        
        # 質問用のテキストクリップ
        try:
            question_clip = TextClip(
                question_text,
                fontsize=80,
                color=self.text_config['colors']['accent'],
                font=self.text_config['font'],
                size=(self.width - 100, None),
                method='caption',
                align='center'
            )
            question_clip = question_clip.with_position(('center', self.height * 0.35))
            question_clip = question_clip.with_duration(duration)
            
            # コンテキスト用のテキストクリップ
            if context_text:
                context_clip = TextClip(
                    context_text,
                    fontsize=50,
                    color=self.text_config['colors']['primary'],
                    font=self.text_config['font'],
                    size=(self.width - 100, None),
                    method='caption',
                    align='center'
                )
                context_clip = context_clip.with_position(('center', self.height * 0.55))
                context_clip = context_clip.with_duration(duration)
                
                composite = CompositeVideoClip([background, question_clip, context_clip])
            else:
                composite = CompositeVideoClip([background, question_clip])
            
            # フェードイン
            composite = composite.with_effects([vfx.FadeIn(0.5)])
            
            return composite
            
        except Exception as e:
            print(f"⚠️ オープニング生成エラー: {e}")
            return background
    
    def _create_choice_sections(
        self,
        question_data: Dict,
        choice_videos: Dict[int, str]
    ) -> List[VideoFileClip]:
        """選択肢セクションを作成"""
        choice_clips = []
        choices = question_data.get('choices', [])
        
        for choice in choices:
            number = choice['number']
            video_path = choice_videos.get(number)
            
            if video_path and os.path.exists(video_path):
                clip = self._create_single_choice(choice, video_path)
                choice_clips.append(clip)
            else:
                print(f"⚠️ 選択肢{number}の動画が見つかりません: {video_path}")
                # フォールバック: 黒画面
                fallback = self._create_fallback_choice(choice)
                choice_clips.append(fallback)
        
        return choice_clips
    
    def _create_single_choice(self, choice: Dict, video_path: str) -> VideoFileClip:
        """1つの選択肢クリップを作成"""
        duration = self.durations['choice']
        
        # AI生成動画を読み込み
        try:
            video = VideoFileClip(video_path)
            
            # 長さを調整
            if video.duration < duration:
                video = video.with_effects([vfx.Loop(duration=duration)])
            else:
                video = video.subclip(0, duration)
            
            # 縦型にリサイズ
            video = video.with_effects([vfx.Resize(height=self.height)])
            
            # 中央でクロップ
            if video.w > self.width:
                x_center = video.w / 2
                x1 = x_center - self.width / 2
                video = video.with_effects([vfx.Crop(x1=x1, width=self.width)])
            
        except Exception as e:
            print(f"⚠️ 動画読み込みエラー: {e}")
            video = ColorClip(
                size=(self.width, self.height),
                color=(20, 20, 20),
                duration=duration
            )
        
        # テキストオーバーレイ
        number = choice['number']
        title = choice['title']
        description = choice.get('description', '')
        
        # 番号バッジ
        try:
            number_text = TextClip(
                f"❶{number}",
                fontsize=100,
                color=self.text_config['colors']['accent'],
                font=self.text_config['font']
            )
            number_text = number_text.with_position((50, 100))
            number_text = number_text.with_duration(duration)
            
            # タイトル
            title_text = TextClip(
                title,
                fontsize=70,
                color=self.text_config['colors']['primary'],
                font=self.text_config['font'],
                size=(self.width - 200, None),
                method='caption',
                align='center',
                bg_color=self.text_config['colors']['background']
            )
            title_text = title_text.with_position(('center', self.height * 0.75))
            title_text = title_text.with_duration(duration)
            
            # 説明文
            if description:
                desc_text = TextClip(
                    description,
                    fontsize=45,
                    color=self.text_config['colors']['primary'],
                    font=self.text_config['font'],
                    size=(self.width - 200, None),
                    method='caption',
                    align='center',
                    bg_color=self.text_config['colors']['background']
                )
                desc_text = desc_text.with_position(('center', self.height * 0.85))
                desc_text = desc_text.with_duration(duration)
                
                composite = CompositeVideoClip([video, number_text, title_text, desc_text])
            else:
                composite = CompositeVideoClip([video, number_text, title_text])
            
            return composite
            
        except Exception as e:
            print(f"⚠️ テキストオーバーレイエラー: {e}")
            return video
    
    def _create_fallback_choice(self, choice: Dict) -> VideoFileClip:
        """フォールバック用の選択肢クリップ"""
        duration = self.durations['choice']
        
        background = ColorClip(
            size=(self.width, self.height),
            color=(20, 20, 20),
            duration=duration
        )
        
        text = f"❶{choice['number']}\n{choice['title']}"
        
        try:
            text_clip = TextClip(
                text,
                fontsize=80,
                color='white',
                font=self.text_config['font'],
                size=(self.width - 100, None),
                method='caption',
                align='center'
            )
            text_clip = text_clip.with_position('center')
            text_clip = text_clip.with_duration(duration)
            
            return CompositeVideoClip([background, text_clip])
        except:
            return background
    
    def _create_ending(self) -> VideoFileClip:
        """エンディングパートを作成"""
        duration = self.durations['ending']
        
        # 背景（黒）
        background = ColorClip(
            size=(self.width, self.height),
            color=(0, 0, 0),
            duration=duration
        )
        
        # エンディングテキスト
        ending_text = "あなたはどれを選んだ？\n\nコメント欄で教えて！"
        
        try:
            text_clip = TextClip(
                ending_text,
                fontsize=70,
                color=self.text_config['colors']['accent'],
                font=self.text_config['font'],
                size=(self.width - 100, None),
                method='caption',
                align='center'
            )
            text_clip = text_clip.with_position('center')
            text_clip = text_clip.with_duration(duration)
            
            composite = CompositeVideoClip([background, text_clip])
            
            # フェードアウト
            composite = composite.with_effects([vfx.FadeOut(0.5)])
            
            return composite
            
        except Exception as e:
            print(f"⚠️ エンディング生成エラー: {e}")
            return background


if __name__ == "__main__":
    # テスト実行
    print("QuestionVideoCreator テストモード")
    
    # テストデータ
    test_question = {
        "question": "1週間耐えたら5億円！どの部屋を選ぶ？",
        "context": "※1週間外出禁止です！",
        "choices": [
            {"number": 1, "title": "極寒の部屋", "description": "氷点下20度"},
            {"number": 2, "title": "灼熱の部屋", "description": "気温50度"},
            {"number": 3, "title": "完全暗闇", "description": "光が一切ない"},
            {"number": 4, "title": "騒音地獄", "description": "24時間大音量"}
        ]
    }
    
    # 動画パス（ダミー）
    test_videos = {
        1: "output/choice_1.mp4",
        2: "output/choice_2.mp4",
        3: "output/choice_3.mp4",
        4: "output/choice_4.mp4"
    }
    
    creator = QuestionVideoCreator()
    
    # 動画が存在する場合のみテスト実行
    if any(os.path.exists(path) for path in test_videos.values()):
        output = "output/test_question_video.mp4"
        creator.create_question_video(test_question, test_videos, output)
    else:
        print("⚠️ テスト動画が見つかりません")
        print("各選択肢の動画を output/choice_1.mp4 〜 choice_4.mp4 に配置してください")
