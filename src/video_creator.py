"""
動画生成モジュール
MoviePyとFFmpegを使用して動画を生成
"""

import os
from typing import Dict, Optional
from moviepy import (
    VideoFileClip, ImageClip, AudioFileClip, 
    TextClip, CompositeVideoClip, concatenate_videoclips
)
from moviepy import vfx
import yaml


class VideoCreator:
    """動画生成クラス"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Args:
            config_path: 設定ファイルのパス
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.video_config = self.config['video']
        self.width = self.video_config['resolution'][0]
        self.height = self.video_config['resolution'][1]
        self.fps = self.video_config['fps']
        self.duration = self.video_config['duration']
    
    def create_video(
        self,
        background_path: str,
        audio_path: str,
        script: str,
        output_path: str,
        genre: str
    ) -> str:
        """
        動画を生成
        
        Args:
            background_path: 背景画像/動画のパス
            audio_path: 音声ファイルのパス
            script: スクリプトテキスト(字幕用)
            output_path: 出力ファイルパス
            genre: ジャンル
            
        Returns:
            生成された動画ファイルのパス
        """
        # 出力ディレクトリを作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 音声を読み込み
        audio = AudioFileClip(audio_path)
        actual_duration = min(audio.duration, self.duration)
        
        # 背景を読み込み
        if background_path.endswith(('.mp4', '.mov', '.avi')):
            # 動画の場合
            background = VideoFileClip(background_path)
            # ループさせて必要な長さにする
            if background.duration < actual_duration:
                n_loops = int(actual_duration / background.duration) + 1
                background = concatenate_videoclips([background] * n_loops)
            background = background.subclip(0, actual_duration)
        else:
            # 画像の場合
            background = ImageClip(background_path, duration=actual_duration)
        
        # 縦型(9:16)にリサイズ
        background = background.with_effects([vfx.Resize(height=self.height)])
        
        # 中央でクロップ
        if background.w > self.width:
            x_center = background.w / 2
            x1 = x_center - self.width / 2
            background = background.with_effects([vfx.Crop(x1=x1, width=self.width)])
        
        # 字幕を追加
        subtitles = self._create_subtitles(script, actual_duration, genre)
        
        # 動画を合成
        video = CompositeVideoClip([background] + subtitles)
        video = video.with_audio(audio)
        video = video.with_duration(actual_duration)
        
        # フェードイン・フェードアウト
        video = video.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])
        
        # 動画を書き出し
        video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            preset='medium',
            threads=4
        )
        
        # クリーンアップ
        video.close()
        audio.close()
        background.close()
        
        print(f"動画を生成しました: {output_path}")
        return output_path
    
    def _create_subtitles(
        self, 
        text: str, 
        duration: float, 
        genre: str
    ) -> list:
        """
        字幕を生成
        
        Args:
            text: 字幕テキスト
            duration: 動画の長さ
            genre: ジャンル
            
        Returns:
            TextClipのリスト
        """
        # ジャンル別のスタイル設定
        styles = {
            'horror': {
                'fontsize': 50,
                'color': 'white',
                'bg_color': 'rgba(0,0,0,0.7)',
                'font': 'Arial-Bold'
            },
            'trivia': {
                'fontsize': 55,
                'color': 'yellow',
                'bg_color': 'rgba(0,0,0,0.6)',
                'font': 'Arial-Bold'
            },
            'satisfying': {
                'fontsize': 52,
                'color': 'white',
                'bg_color': 'rgba(255,100,100,0.7)',
                'font': 'Arial-Bold'
            }
        }
        
        style = styles.get(genre, styles['trivia'])
        
        # テキストを分割(改行で)
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # 各行の表示時間を計算
        time_per_line = duration / len(lines) if lines else duration
        
        subtitles = []
        for i, line in enumerate(lines):
            start_time = i * time_per_line
            
            # 長い行は折り返し
            if len(line) > 20:
                # 20文字ごとに改行
                wrapped_line = '\n'.join([
                    line[j:j+20] for j in range(0, len(line), 20)
                ])
            else:
                wrapped_line = line
            
            try:
                txt_clip = TextClip(
                    wrapped_line,
                    fontsize=style['fontsize'],
                    color=style['color'],
                    font=style['font'],
                    method='caption',
                    size=(self.width - 100, None),
                    align='center'
                )
                
                # 背景を追加
                txt_clip = txt_clip.on_color(
                    size=(self.width - 80, txt_clip.h + 20),
                    color=style['bg_color'],
                    pos='center'
                )
                
                # 位置と時間を設定
                txt_clip = txt_clip.set_position(('center', self.height * 0.7))
                txt_clip = txt_clip.set_start(start_time)
                txt_clip = txt_clip.set_duration(time_per_line)
                
                subtitles.append(txt_clip)
            except Exception as e:
                print(f"字幕生成エラー (行 {i}): {e}")
                continue
        
        return subtitles


if __name__ == "__main__":
    # テスト実行
    import sys
    
    creator = VideoCreator()
    
    if len(sys.argv) >= 5:
        background = sys.argv[1]
        audio = sys.argv[2]
        script = sys.argv[3]
        output = sys.argv[4]
        genre = sys.argv[5] if len(sys.argv) > 5 else 'trivia'
        
        creator.create_video(background, audio, script, output, genre)
    else:
        print("使用方法: python video_creator.py <background> <audio> <script> <output> [genre]")
