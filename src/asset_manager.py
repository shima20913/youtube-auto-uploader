"""
素材管理モジュール
Pexels APIを使用してフリー素材を取得・管理
"""

import os
import requests
import hashlib
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class AssetManager:
    """フリー素材の取得と管理"""
    
    def __init__(self, cache_dir: str = "./cache"):
        """
        Args:
            cache_dir: キャッシュディレクトリ
        """
        self.api_key = os.getenv("PEXELS_API_KEY")
        
        if not self.api_key:
            raise ValueError("PEXELS_API_KEY が設定されていません")
        
        self.cache_dir = cache_dir
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {"Authorization": self.api_key}
        
        # キャッシュディレクトリを作成
        os.makedirs(cache_dir, exist_ok=True)
    
    def search_videos(
        self, 
        query: str, 
        orientation: str = "portrait",
        size: str = "medium",
        per_page: int = 10
    ) -> List[Dict]:
        """
        動画素材を検索
        
        Args:
            query: 検索クエリ
            orientation: 向き (portrait, landscape, square)
            size: サイズ (large, medium, small)
            per_page: 取得件数
            
        Returns:
            動画情報のリスト
        """
        url = f"{self.base_url}/videos/search"
        params = {
            "query": query,
            "orientation": orientation,
            "size": size,
            "per_page": per_page
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get("videos", [])
    
    def search_photos(
        self, 
        query: str, 
        orientation: str = "portrait",
        per_page: int = 10
    ) -> List[Dict]:
        """
        画像素材を検索
        
        Args:
            query: 検索クエリ
            orientation: 向き (portrait, landscape, square)
            per_page: 取得件数
            
        Returns:
            画像情報のリスト
        """
        url = f"{self.base_url}/search"
        params = {
            "query": query,
            "orientation": orientation,
            "per_page": per_page
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get("photos", [])
    
    def download_asset(
        self, 
        url: str, 
        filename: Optional[str] = None
    ) -> str:
        """
        素材をダウンロード
        
        Args:
            url: ダウンロードURL
            filename: 保存ファイル名 (Noneの場合はURLからハッシュ生成)
            
        Returns:
            ダウンロードしたファイルのパス
        """
        if filename is None:
            # URLからハッシュを生成してファイル名を作成
            url_hash = hashlib.md5(url.encode()).hexdigest()
            ext = url.split('.')[-1].split('?')[0]
            filename = f"{url_hash}.{ext}"
        
        filepath = os.path.join(self.cache_dir, filename)
        
        # すでにキャッシュされている場合はスキップ
        if os.path.exists(filepath):
            print(f"キャッシュから読み込み: {filepath}")
            return filepath
        
        # ダウンロード
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"素材をダウンロードしました: {filepath}")
        return filepath
    
    def get_video_for_genre(
        self, 
        keywords: List[str], 
        genre: str
    ) -> str:
        """
        ジャンルに応じた動画素材を取得
        
        Args:
            keywords: 検索キーワードリスト
            genre: ジャンル
            
        Returns:
            ダウンロードした動画ファイルのパス
        """
        # キーワードを組み合わせて検索
        query = " ".join(keywords[:2])  # 最初の2つのキーワードを使用
        
        videos = self.search_videos(query, orientation="portrait")
        
        if not videos:
            # 見つからない場合はデフォルトキーワードで検索
            default_queries = {
                'horror': 'dark mysterious',
                'trivia': 'abstract colorful',
                'satisfying': 'nature peaceful'
            }
            query = default_queries.get(genre, 'abstract')
            videos = self.search_videos(query, orientation="portrait")
        
        if not videos:
            raise ValueError(f"動画素材が見つかりませんでした: {query}")
        
        # 最初の動画のHD版をダウンロード
        video = videos[0]
        video_files = video.get('video_files', [])
        
        # 縦型(portrait)のHD動画を探す
        hd_video = None
        for vf in video_files:
            if vf.get('quality') == 'hd' and vf.get('width', 0) < vf.get('height', 0):
                hd_video = vf
                break
        
        # HD動画がない場合は最初の縦型動画を使用
        if not hd_video:
            for vf in video_files:
                if vf.get('width', 0) < vf.get('height', 0):
                    hd_video = vf
                    break
        
        if not hd_video:
            hd_video = video_files[0]
        
        return self.download_asset(hd_video['link'])
    
    def get_image_for_genre(
        self, 
        keywords: List[str], 
        genre: str
    ) -> str:
        """
        ジャンルに応じた画像素材を取得
        
        Args:
            keywords: 検索キーワードリスト
            genre: ジャンル
            
        Returns:
            ダウンロードした画像ファイルのパス
        """
        # キーワードを組み合わせて検索
        query = " ".join(keywords[:2])
        
        photos = self.search_photos(query, orientation="portrait")
        
        if not photos:
            # 見つからない場合はデフォルトキーワードで検索
            default_queries = {
                'horror': 'dark atmosphere',
                'trivia': 'books knowledge',
                'satisfying': 'happy people'
            }
            query = default_queries.get(genre, 'abstract')
            photos = self.search_photos(query, orientation="portrait")
        
        if not photos:
            raise ValueError(f"画像素材が見つかりませんでした: {query}")
        
        # 最初の画像の大サイズをダウンロード
        photo = photos[0]
        image_url = photo['src']['large2x']
        
        return self.download_asset(image_url)


if __name__ == "__main__":
    # テスト実行
    import sys
    
    manager = AssetManager()
    
    if len(sys.argv) > 1:
        genre = sys.argv[1]
        keywords = ['dark', 'mysterious']
        
        print(f"ジャンル: {genre}")
        print(f"キーワード: {keywords}")
        
        # 画像を取得
        image_path = manager.get_image_for_genre(keywords, genre)
        print(f"画像: {image_path}")
    else:
        print("使用方法: python asset_manager.py <genre>")
