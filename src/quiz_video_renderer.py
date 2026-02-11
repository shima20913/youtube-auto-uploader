"""
QuizWithVideos用のレンダラー（バイリンガル対応）
横型AI動画を使ったクイズ形式の動画を生成
"""

import subprocess
import json
import os
from typing import Dict, List, Optional


class QuizVideoRenderer:
    """クイズ形式の動画レンダリングクラス（バイリンガル）"""
    
    def __init__(self, remotion_dir: str = "remotion"):
        self.remotion_dir = remotion_dir
    
    def render_quiz_video(
        self,
        question: str,
        question_en: str,
        choices: List[Dict[str, str]],  # [{number: 1, text: "溶岩の中", textEn: "In the lava", videoPath: "..."}]
        end_message: str,
        end_message_en: str,
        output_path: str
    ) -> bool:
        """
        クイズ動画をレンダリング（バイリンガル）
        
        Args:
            question: 質問文（日本語）
            question_en: 質問文（英語）
            choices: 選択肢リスト
            end_message: 最後のメッセージ（日本語）
            end_message_en: 最後のメッセージ（英語）
            output_path: 出力ファイルパス
            
        Returns:
            成功した場合True
        """
        print(f"🎬 クイズ動画生成開始: {question}")
        print(f"   ({question_en})")
        
        # 出力ディレクトリを作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # データ構築
        quiz_data = {
            "question": question,
            "questionEn": question_en,
            "choices": choices,
            "endMessage": end_message,
            "endMessageEn": end_message_en
        }
        
        # Remotionレンダリング
        cmd = [
            "npx",
            "remotion",
            "render",
            "QuizWithVideos",
            output_path,
            "--props",
            json.dumps({"data": quiz_data}),
        ]
        
        try:
            print("⏳ レンダリング中...")
            result = subprocess.run(
                cmd,
                cwd=self.remotion_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分
            )
            
            if result.returncode == 0:
                print(f"✅ 動画生成完了: {output_path}")
                return True
            else:
                print(f"❌ レンダリング失敗:")
                print(f"STDERR: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ エラー発生: {e}")
            return False


if __name__ == "__main__":
    # テスト実行（バイリンガル）
    renderer = QuizVideoRenderer()
    
    test_choices = [
        {"number": 1, "text": "溶岩の中", "textEn": "In the Lava", "videoPath": "videos/lava.mp4"},
        {"number": 2, "text": "氷の部屋", "textEn": "Ice Room", "videoPath": "videos/ice.mp4"},
        {"number": 3, "text": "宇宙空間", "textEn": "Outer Space", "videoPath": "videos/space.mp4"},
        {"number": 4, "text": "水中都市", "textEn": "Underwater City", "videoPath": "videos/underwater.mp4"},
    ]
    
    success = renderer.render_quiz_video(
        question="一週間過ごすなら？",
        question_en="Where would you spend a week?",
        choices=test_choices,
        end_message="あなたはどこに住みたいと思いましたか？\n感想はコメント欄へ！",
        end_message_en="Where would you like to live?\nComment below!",
        output_path="output/quiz_bilingual_test.mp4"
    )
    
    if success:
        print("\n✅ テスト成功！")
    else:
        print("\n❌ テスト失敗")
