"""
Instagram Reels 自動投稿モジュール
instagrapi（非公式ライブラリ）を使用
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class InstagramUploader:
    """Instagram Reels 投稿クラス"""

    def __init__(self):
        self.username = os.getenv("INSTAGRAM_USERNAME")
        self.password = os.getenv("INSTAGRAM_PASSWORD")

        if not self.username or not self.password:
            raise ValueError(
                "INSTAGRAM_USERNAME と INSTAGRAM_PASSWORD が設定されていません"
            )

        # セッションキャッシュファイル
        self.session_file = Path(__file__).parent.parent / "output" / "instagram_session.json"
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

        self._client = None

    def _get_client(self):
        """instagrapiクライアントを取得（遅延初期化）"""
        if self._client is not None:
            return self._client

        try:
            from instagrapi import Client
        except ImportError:
            raise ImportError(
                "instagrapi がインストールされていません。"
                "'pip install instagrapi' を実行してください。"
            )

        cl = Client()

        # セッションファイルがあれば再利用
        if self.session_file.exists():
            try:
                cl.load_settings(self.session_file)
                cl.login(self.username, self.password)
                print("✅ Instagram: セッションキャッシュから認証成功")
                self._client = cl
                return cl
            except Exception:
                print("⚠️  Instagram: セッションキャッシュ期限切れ。再ログインします")
                self.session_file.unlink(missing_ok=True)

        # 新規ログイン
        cl.login(self.username, self.password)
        cl.dump_settings(self.session_file)
        print("✅ Instagram: ログイン成功")
        self._client = cl
        return cl

    def upload_reel(self, video_path: str, caption: str) -> str:
        """
        Instagram Reels に動画を投稿

        Args:
            video_path: 動画ファイルのパス
            caption: キャプション（ハッシュタグを含む）

        Returns:
            投稿URL（例: https://www.instagram.com/reel/XXXXXXX/）
        """
        cl = self._get_client()
        video = Path(video_path)

        if not video.exists():
            raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")

        print(f"📸 Instagram: Reels アップロード中... ({video.name})")

        media = cl.clip_upload(
            video,
            caption=caption,
        )

        post_url = f"https://www.instagram.com/reel/{media.code}/"
        print(f"✅ Instagram: 投稿完了 → {post_url}")
        return post_url
