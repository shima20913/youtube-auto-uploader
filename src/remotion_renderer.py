"""
Remotionレンダラー - Python連携モジュール
Discord BotとRemotion動画生成を橋渡しする
"""

import subprocess
import json
import os
from typing import Dict, Optional
from datetime import datetime
import random


class RemotionRenderer:
    """Remotionを使用した動画レンダリングクラス"""
    
    def __init__(self, remotion_dir: str = "remotion"):
        """
        Args:
            remotion_dir: Remotionプロジェクトのディレクトリ
        """
        self.remotion_dir = remotion_dir
        self.templates = [
            "QuestionTemplate1",
            # 将来的に追加
            # "QuestionTemplate2",
            # "QuestionTemplate3",
        ]
    
    def render_question_video(
        self,
        question_data: Dict,
        output_path: str,
        template: Optional[str] = None
    ) -> bool:
        """
        質問動画をレンダリング
        
        Args:
            question_data: 質問データ
                {
                    "id": "xxx",
                    "question": "質問文",
                    "options": ["選択肢1", "選択肢2"]
                }
            output_path: 出力ファイルパス
            template: テンプレート名（Noneの場合は日替わり）
            
        Returns:
            成功した場合True
        """
        print(f"🎬 Remotion動画生成開始: {question_data.get('question', 'Unknown')[:30]}...")
        
        # テンプレート選択（日替わり）
        if template is None:
            daily_seed = datetime.now().strftime("%Y%m%d")
            random.seed(daily_seed)
            template = random.choice(self.templates)
            print(f"📅 今日のテンプレート: {template}")
        
        # 出力ディレクトリを作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Remotionレンダリングコマンド
        cmd = [
            "npx",
            "remotion",
            "render",
            template,
            output_path,
            "--props",
            json.dumps({"data": question_data}),
        ]
        
        try:
            print("⏳ レンダリング中...")
            result = subprocess.run(
                cmd,
                cwd=self.remotion_dir,
                capture_output=True,
                text=True,
                timeout=180  # 3分タイムアウト
            )
            
            if result.returncode == 0:
                print(f"✅ 動画生成完了: {output_path}")
                return True
            else:
                print(f"❌ レンダリング失敗:")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏱️ レンダリングタイムアウト（3分超過）")
            return False
        except Exception as e:
            print(f"❌ エラー発生: {e}")
            return False
    
    def preview_in_studio(self):
        """Remotion Studioでプレビュー（開発用）"""
        print("🎨 Remotion Studioを起動中...")
        subprocess.run(
            ["npm", "run", "start"],
            cwd=self.remotion_dir
        )


if __name__ == "__main__":
    # テスト実行
    renderer = RemotionRenderer()
    
    test_data = {
        "id": "test-001",
        "question": "あなたはどっち派？",
        "options": ["朝型人間", "夜型人間"]
    }
    
    output = "output/test_remotion_video.mp4"
    
    success = renderer.render_question_video(test_data, output)
    
    if success:
        print(f"\n✅ テスト成功！")
        print(f"📹 動画: {output}")
    else:
        print(f"\n❌ テスト失敗")
