"""
TikTok 自動投稿モジュール
tiktok-uploader（非公式ライブラリ）を使用

【セッションIDの取得方法】
1. PCブラウザでTikTok (tiktok.com) にログイン
2. F12キーでDevToolsを開く
3. Application タブ → Cookies → https://www.tiktok.com
4. 「sessionid」の値をコピー
5. .envの TIKTOK_SESSION_ID に設定
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class TikTokUploader:
    """TikTok 動画投稿クラス"""

    def __init__(self):
        self.session_id = os.getenv("TIKTOK_SESSION_ID")

        if not self.session_id:
            raise ValueError(
                "TIKTOK_SESSION_ID が設定されていません。\n"
                "取得方法: PCブラウザでTikTokにログイン → F12 → "
                "Application → Cookies → sessionid の値をコピー"
            )

    def upload_video(self, video_path: str, title: str, tags: list = None) -> bool:
        """
        TikTokに動画を投稿

        Args:
            video_path: 動画ファイルのパス
            title: 動画のタイトル（キャプション）
            tags: ハッシュタグリスト（例: ["質問", "選択式"]）

        Returns:
            成功した場合True
        """
        try:
            from tiktok_uploader.upload import upload_video
        except ImportError:
            raise ImportError(
                "tiktok-uploader がインストールされていません。\n"
                "'pip install tiktok-uploader' を実行してください。"
            )

        video = Path(video_path)
        if not video.exists():
            raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")

        # ハッシュタグをキャプションに追加
        caption = title
        if tags:
            hashtags = " ".join(f"#{tag}" for tag in tags)
            caption = f"{title}\n{hashtags}"

        print(f"🎵 TikTok: 動画アップロード中... ({video.name})")

        # Cookiesをdict形式で渡す
        cookies = [
            {
                "name": "sessionid",
                "value": self.session_id,
                "domain": ".tiktok.com",
                "path": "/",
            }
        ]

        upload_video(
            str(video),
            description=caption,
            cookies=cookies,
        )

        print("✅ TikTok: 投稿完了")
        return True
