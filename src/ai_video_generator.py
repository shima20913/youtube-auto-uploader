"""
AI動画生成モジュール
LumaAI Ray3.14 APIを使用して高品質な動画を生成
"""

import os
import time
import requests
import asyncio
from typing import Dict, List, Optional
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()


class AIVideoGenerator:
    """LumaAI API を使用した動画生成クラス"""
    
    def __init__(self):
        """初期化"""
        self.api_key = os.getenv("LUMAAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("LUMAAI_API_KEY が設定されていません")
        
        self.base_url = "https://api.lumalabs.ai/v1/generations"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # デフォルト設定
        self.default_config = {
            "aspect_ratio": "9:16",  # YouTubeショート用（縦型）
            "duration": 5,  # 秒
        }
        
        # リトライ設定
        self.max_retries = 3
        self.retry_delay = 10  # 秒
        
        # タイムアウト設定
        self.generation_timeout = 300  # 5分
    
    def generate_video(
        self,
        prompt: str,
        output_path: str,
        duration: int = 5
    ) -> Optional[str]:
        """
        プロンプトから動画を生成
        
        Args:
            prompt: 動画生成用のプロンプト
            output_path: 出力ファイルパス
            duration: 動画の長さ（秒）
            
        Returns:
            生成された動画のパス（失敗時はNone）
        """
        print(f"🎬 動画生成開始: {prompt[:50]}...")
        
        for attempt in range(self.max_retries):
            try:
                # 生成リクエストを送信
                generation_id = self._create_generation(prompt, duration)
                
                if not generation_id:
                    print(f"⚠️ 生成リクエスト失敗（試行 {attempt + 1}/{self.max_retries}）")
                    time.sleep(self.retry_delay)
                    continue
                
                # 生成完了を待機
                video_url = self._wait_for_completion(generation_id)
                
                if not video_url:
                    print(f"⚠️ 生成タイムアウト（試行 {attempt + 1}/{self.max_retries}）")
                    time.sleep(self.retry_delay)
                    continue
                
                # 動画をダウンロード
                success = self._download_video(video_url, output_path)
                
                if success:
                    print(f"✅ 動画生成完了: {output_path}")
                    return output_path
                else:
                    print(f"⚠️ ダウンロード失敗（試行 {attempt + 1}/{self.max_retries}）")
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                print(f"❌ エラー発生: {e}（試行 {attempt + 1}/{self.max_retries}）")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        print(f"❌ 動画生成失敗: 最大試行回数を超えました")
        return None
    
    def _create_generation(self, prompt: str, duration: int) -> Optional[str]:
        """
        動画生成リクエストを作成
        
        Args:
            prompt: プロンプト
            duration: 動画の長さ
            
        Returns:
            生成ID
        """
        payload = {
            "prompt": prompt,
            "aspect_ratio": self.default_config["aspect_ratio"],
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                generation_id = data.get("id")
                print(f"📝 生成ID: {generation_id}")
                return generation_id
            else:
                print(f"❌ API エラー: {response.status_code}")
                print(f"レスポンス: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ リクエストエラー: {e}")
            return None
    
    def _wait_for_completion(self, generation_id: str) -> Optional[str]:
        """
        動画生成の完了を待機
        
        Args:
            generation_id: 生成ID
            
        Returns:
            動画URL
        """
        start_time = time.time()
        poll_interval = 5  # 5秒ごとにチェック
        
        while time.time() - start_time < self.generation_timeout:
            try:
                response = requests.get(
                    f"{self.base_url}/{generation_id}",
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    state = data.get("state")
                    
                    print(f"⏳ 状態: {state}")
                    
                    if state == "completed":
                        video_url = data.get("assets", {}).get("video")
                        if video_url:
                            print(f"✅ 生成完了！")
                            return video_url
                    elif state == "failed":
                        print(f"❌ 生成失敗")
                        return None
                    
                    # 引き続き待機
                    time.sleep(poll_interval)
                else:
                    print(f"❌ ステータス確認エラー: {response.status_code}")
                    time.sleep(poll_interval)
                    
            except Exception as e:
                print(f"❌ ポーリングエラー: {e}")
                time.sleep(poll_interval)
        
        print(f"⏱️ タイムアウト: {self.generation_timeout}秒経過")
        return None
    
    def _download_video(self, video_url: str, output_path: str) -> bool:
        """
        動画をダウンロード
        
        Args:
            video_url: 動画URL
            output_path: 出力パス
            
        Returns:
            成功した場合True
        """
        try:
            print(f"⬇️ ダウンロード中...")
            
            response = requests.get(video_url, stream=True, timeout=60)
            
            if response.status_code == 200:
                # ディレクトリが存在しない場合は作成
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✅ ダウンロード完了: {output_path}")
                return True
            else:
                print(f"❌ ダウンロードエラー: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ダウンロード例外: {e}")
            return False
    
    def generate_multiple_videos(
        self,
        prompts: List[str],
        output_dir: str,
        duration: int = 5
    ) -> Dict[int, Optional[str]]:
        """
        複数の動画を並列生成
        
        Args:
            prompts: プロンプトのリスト
            output_dir: 出力ディレクトリ
            duration: 各動画の長さ
            
        Returns:
            {インデックス: 動画パス} の辞書
        """
        print(f"🎬 {len(prompts)}本の動画を並列生成します...")
        
        results = {}
        
        # 並列生成（最大4並列）
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_index = {}
            
            for i, prompt in enumerate(prompts):
                output_path = os.path.join(output_dir, f"choice_{i+1}.mp4")
                future = executor.submit(
                    self.generate_video,
                    prompt,
                    output_path,
                    duration
                )
                future_to_index[future] = i + 1
            
            # 結果を収集
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    video_path = future.result()
                    results[index] = video_path
                    print(f"✅ 選択肢{index}の動画: {'完了' if video_path else '失敗'}")
                except Exception as e:
                    print(f"❌ 選択肢{index}で例外発生: {e}")
                    results[index] = None
        
        success_count = sum(1 for v in results.values() if v is not None)
        print(f"\n📊 結果: {success_count}/{len(prompts)} 本の動画を生成")
        
        return results


if __name__ == "__main__":
    # テスト実行
    import sys
    
    generator = AIVideoGenerator()
    
    # テストプロンプト
    test_prompt = "A freezing cold ice room with frost-covered walls, dim blue lighting, icy atmosphere, cinematic, ultra-realistic, 4k"
    output_path = "output/test_video.mp4"
    
    if len(sys.argv) > 1:
        test_prompt = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    
    print(f"テストプロンプト: {test_prompt}")
    print(f"出力先: {output_path}\n")
    
    result = generator.generate_video(test_prompt, output_path)
    
    if result:
        print(f"\n✅ 成功: {result}")
    else:
        print(f"\n❌ 失敗")
