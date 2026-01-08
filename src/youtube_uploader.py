"""
YouTube投稿モジュール
YouTube Data API v3を使用して動画をアップロード
"""

import os
import pickle
from typing import Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()


class YouTubeUploader:
    """YouTube動画アップローダー"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_file: str = 'client_secret.json'):
        """
        Args:
            credentials_file: OAuth 2.0認証情報ファイル
        """
        self.credentials_file = credentials_file
        self.credentials = None
        self.youtube = None
        
        self._authenticate()
    
    def _authenticate(self):
        """YouTube APIの認証"""
        token_file = 'token.pickle'
        
        # 保存された認証情報を読み込み
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                self.credentials = pickle.load(token)
        
        # 認証情報が無効または存在しない場合
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                # トークンをリフレッシュ
                self.credentials.refresh(Request())
            else:
                # 新規認証
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"認証情報ファイルが見つかりません: {self.credentials_file}\n"
                        "Google Cloud Consoleから client_secret.json をダウンロードしてください。"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, 
                    self.SCOPES
                )
                self.credentials = flow.run_local_server(port=0)
            
            # 認証情報を保存
            with open(token_file, 'wb') as token:
                pickle.dump(self.credentials, token)
        
        # YouTube APIクライアントを構築
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
        print("YouTube APIの認証に成功しました")
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list,
        category_id: str = "24",
        privacy_status: str = "public"
    ) -> Dict:
        """
        動画をアップロード
        
        Args:
            video_path: 動画ファイルのパス
            title: 動画タイトル
            description: 動画の説明
            tags: タグのリスト
            category_id: カテゴリID (24 = Entertainment)
            privacy_status: 公開設定 (public, private, unlisted)
            
        Returns:
            アップロード結果
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
        
        # メタデータを設定
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # メディアファイルを準備
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True,
            chunksize=1024*1024  # 1MB chunks
        )
        
        # アップロードリクエストを作成
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        # アップロードを実行
        print(f"動画をアップロード中: {title}")
        response = None
        
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"アップロード進捗: {progress}%")
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"アップロード完了!")
        print(f"動画URL: {video_url}")
        
        return {
            'video_id': video_id,
            'video_url': video_url,
            'title': title,
            'response': response
        }
    
    def upload_short(
        self,
        video_path: str,
        title: str,
        description: str,
        hashtags: str
    ) -> Dict:
        """
        YouTubeショート動画をアップロード
        
        Args:
            video_path: 動画ファイルのパス
            title: 動画タイトル
            description: 動画の説明
            hashtags: ハッシュタグ
            
        Returns:
            アップロード結果
        """
        # ショート動画用の説明文を作成
        full_description = f"{description}\n\n{hashtags}\n\n#Shorts"
        
        # タグを抽出
        tags = [tag.strip('#') for tag in hashtags.split() if tag.startswith('#')]
        tags.append('Shorts')
        
        return self.upload_video(
            video_path=video_path,
            title=title,
            description=full_description,
            tags=tags,
            category_id="24",
            privacy_status="public"
        )


if __name__ == "__main__":
    # テスト実行
    import sys
    
    if len(sys.argv) >= 4:
        uploader = YouTubeUploader()
        
        video_path = sys.argv[1]
        title = sys.argv[2]
        description = sys.argv[3]
        hashtags = sys.argv[4] if len(sys.argv) > 4 else "#テスト"
        
        result = uploader.upload_short(video_path, title, description, hashtags)
        print(f"\n結果: {result}")
    else:
        print("使用方法: python youtube_uploader.py <video_path> <title> <description> [hashtags]")
