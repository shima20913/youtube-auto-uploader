"""
音声合成モジュール
Google Cloud Text-to-Speechを使用してテキストから高品質な音声を生成
"""

import os
from google.cloud import texttospeech
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class TTSEngine:
    """テキスト読み上げエンジン(Google Cloud TTS)"""
    
    def __init__(self, language_code: str = 'ja-JP'):
        """
        Args:
            language_code: 言語コード (デフォルト: 'ja-JP')
        """
        self.language_code = language_code
        
        # APIキーまたはサービスアカウントキーを設定
        api_key = os.getenv('GOOGLE_CLOUD_TTS_API_KEY')
        if api_key:
            # APIキーを使用
            self.client = texttospeech.TextToSpeechClient(
                client_options={"api_key": api_key}
            )
        else:
            # サービスアカウントキー(GOOGLE_APPLICATION_CREDENTIALS)を使用
            self.client = texttospeech.TextToSpeechClient()
    
    def text_to_speech(
        self, 
        text: str, 
        output_path: str,
        voice_name: Optional[str] = None,
        speaking_rate: float = 1.0,
        pitch: float = 0.0
    ) -> str:
        """
        テキストから音声ファイルを生成
        
        Args:
            text: 読み上げるテキスト
            output_path: 出力ファイルパス
            voice_name: 音声名 (例: 'ja-JP-Neural2-B')
            speaking_rate: 話速 (0.25〜4.0, デフォルト: 1.0)
            pitch: ピッチ (-20.0〜20.0, デフォルト: 0.0)
            
        Returns:
            生成された音声ファイルのパス
        """
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # デフォルトの音声名
        if voice_name is None:
            voice_name = 'ja-JP-Neural2-B'  # 女性の声
        
        # 入力テキストを設定
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # 音声パラメータを設定
        voice = texttospeech.VoiceSelectionParams(
            language_code=self.language_code,
            name=voice_name
        )
        
        # オーディオ設定
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=pitch
        )
        
        # 音声合成を実行
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # 音声ファイルを保存
        with open(output_path, 'wb') as out:
            out.write(response.audio_content)
        
        print(f"音声ファイルを生成しました: {output_path}")
        return output_path
    
    def generate_for_genre(
        self, 
        text: str, 
        genre: str, 
        output_path: str
    ) -> str:
        """
        ジャンルに応じた音声を生成
        
        Args:
            text: 読み上げるテキスト
            genre: ジャンル (horror, trivia, satisfying)
            output_path: 出力ファイルパス
            
        Returns:
            生成された音声ファイルのパス
        """
        # ジャンル別の設定
        genre_settings = {
            'horror': {
                'voice_name': 'ja-JP-Neural2-C',  # 男性の低い声
                'speaking_rate': 0.85,             # やや遅め
                'pitch': -5.0                      # 低いピッチ
            },
            'trivia': {
                'voice_name': 'ja-JP-Neural2-B',  # 女性の明るい声
                'speaking_rate': 1.0,              # 標準速度
                'pitch': 2.0                       # やや高めのピッチ
            },
            'satisfying': {
                'voice_name': 'ja-JP-Neural2-B',  # 女性の元気な声
                'speaking_rate': 1.1,              # やや速め
                'pitch': 3.0                       # 高めのピッチ
            }
        }
        
        settings = genre_settings.get(genre, genre_settings['trivia'])
        
        return self.text_to_speech(
            text=text,
            output_path=output_path,
            voice_name=settings['voice_name'],
            speaking_rate=settings['speaking_rate'],
            pitch=settings['pitch']
        )


if __name__ == "__main__":
    # テスト実行
    import sys
    
    engine = TTSEngine()
    
    test_text = "これはGoogle Cloud Text-to-Speechのテスト音声です。高品質なAI音声で、より自然な読み上げが可能になりました。"
    output = "test_output.mp3"
    
    if len(sys.argv) > 1:
        genre = sys.argv[1]
        print(f"ジャンル: {genre}")
        engine.generate_for_genre(test_text, genre, output)
    else:
        engine.text_to_speech(test_text, output)
    
    print(f"テスト音声を生成しました: {output}")
