"""
コンテンツ生成モジュール
Gemini APIを使用してジャンル別のスクリプトを生成
"""

import json
import random
import os
from typing import Dict, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class ContentGenerator:
    """コンテンツ生成の基底クラス"""
    
    def __init__(self, genre: str):
        """
        Args:
            genre: ジャンル (horror, trivia, satisfying)
        """
        self.genre = genre
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY が設定されていません")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # プロンプトテンプレートの読み込み
        template_path = f"templates/{genre}_prompts.json"
        with open(template_path, 'r', encoding='utf-8') as f:
            self.templates = json.load(f)
    
    def generate_content(self) -> Dict[str, str]:
        """
        コンテンツを生成
        
        Returns:
            Dict containing title, script, description, hashtags
        """
        # ランダムにテーマを選択
        template = random.choice(self.templates)
        theme = random.choice(template['themes'])
        
        # プロンプトを作成
        prompt = template['prompt_template'].format(theme=theme)
        
        # Gemini APIでコンテンツ生成
        response = self.model.generate_content(prompt)
        content = response.text
        
        # レスポンスをパース
        parsed_content = self._parse_response(content)
        
        # キーワードを追加(素材検索用)
        parsed_content['keywords'] = template['keywords']
        
        return parsed_content
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """
        Geminiのレスポンスをパース
        
        Args:
            response: Geminiからのレスポンステキスト
            
        Returns:
            パースされたコンテンツ
        """
        lines = response.strip().split('\n')
        result = {
            'title': '',
            'script': '',
            'description': '',
            'hashtags': ''
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('タイトル:'):
                result['title'] = line.replace('タイトル:', '').strip()
            elif line.startswith('スクリプト:'):
                current_section = 'script'
            elif line.startswith('説明文:'):
                current_section = 'description'
            elif line.startswith('ハッシュタグ:'):
                result['hashtags'] = line.replace('ハッシュタグ:', '').strip()
                current_section = None
            elif current_section and line:
                if current_section == 'script':
                    result['script'] += line + '\n'
                elif current_section == 'description':
                    result['description'] += line + '\n'
        
        # スクリプトと説明文の末尾の改行を削除
        result['script'] = result['script'].strip()
        result['description'] = result['description'].strip()
        
        return result


class HorrorGenerator(ContentGenerator):
    """ホラー系コンテンツ生成"""
    
    def __init__(self):
        super().__init__('horror')


class TriviaGenerator(ContentGenerator):
    """雑学系コンテンツ生成"""
    
    def __init__(self):
        super().__init__('trivia')


class SatisfyingGenerator(ContentGenerator):
    """スカッと系コンテンツ生成"""
    
    def __init__(self):
        super().__init__('satisfying')


def get_generator(genre: str) -> ContentGenerator:
    """
    ジャンルに応じたジェネレーターを取得
    
    Args:
        genre: ジャンル名
        
    Returns:
        ContentGeneratorインスタンス
    """
    generators = {
        'horror': HorrorGenerator,
        'trivia': TriviaGenerator,
        'satisfying': SatisfyingGenerator
    }
    
    if genre not in generators:
        raise ValueError(f"未対応のジャンル: {genre}")
    
    return generators[genre]()


if __name__ == "__main__":
    # テスト実行
    import sys
    
    if len(sys.argv) > 1:
        genre = sys.argv[1]
    else:
        genre = 'horror'
    
    print(f"ジャンル: {genre}")
    generator = get_generator(genre)
    content = generator.generate_content()
    
    print("\n=== 生成されたコンテンツ ===")
    print(f"タイトル: {content['title']}")
    print(f"\nスクリプト:\n{content['script']}")
    print(f"\n説明文:\n{content['description']}")
    print(f"\nハッシュタグ: {content['hashtags']}")
