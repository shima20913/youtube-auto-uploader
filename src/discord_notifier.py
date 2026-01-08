"""
Discord通知モジュール
Webhookを使用してDiscordに通知を送信
"""

import os
from typing import Dict, Optional
from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv

load_dotenv()


class DiscordNotifier:
    """Discord通知クラス"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Args:
            webhook_url: Discord Webhook URL
        """
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        
        if not self.webhook_url:
            raise ValueError("DISCORD_WEBHOOK_URL が設定されていません")
    
    def send_notification(
        self,
        title: str,
        description: str,
        color: str = "03b2f8",
        fields: Optional[list] = None,
        thumbnail_url: Optional[str] = None
    ) -> bool:
        """
        Discord通知を送信
        
        Args:
            title: 通知タイトル
            description: 通知内容
            color: 埋め込みの色 (16進数)
            fields: 追加フィールド
            thumbnail_url: サムネイル画像URL
            
        Returns:
            送信成功かどうか
        """
        webhook = DiscordWebhook(url=self.webhook_url)
        
        # 埋め込みメッセージを作成
        embed = DiscordEmbed(
            title=title,
            description=description,
            color=color
        )
        
        # サムネイルを設定
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        
        # フィールドを追加
        if fields:
            for field in fields:
                embed.add_embed_field(
                    name=field.get('name', ''),
                    value=field.get('value', ''),
                    inline=field.get('inline', False)
                )
        
        # タイムスタンプを追加
        embed.set_timestamp()
        
        webhook.add_embed(embed)
        
        # 送信
        response = webhook.execute()
        
        if response.status_code == 200:
            print("Discord通知を送信しました")
            return True
        else:
            print(f"Discord通知の送信に失敗しました: {response.status_code}")
            return False
    
    def notify_upload_success(
        self,
        video_url: str,
        title: str,
        genre: str,
        thumbnail_url: Optional[str] = None
    ) -> bool:
        """
        動画アップロード成功を通知
        
        Args:
            video_url: 動画URL
            title: 動画タイトル
            genre: ジャンル
            thumbnail_url: サムネイル画像URL
            
        Returns:
            送信成功かどうか
        """
        # ジャンル別の色設定
        genre_colors = {
            'horror': '8B0000',      # ダークレッド
            'trivia': 'FFD700',      # ゴールド
            'satisfying': 'FF69B4'   # ホットピンク
        }
        
        # ジャンル別の絵文字
        genre_emojis = {
            'horror': '👻',
            'trivia': '📚',
            'satisfying': '😊'
        }
        
        color = genre_colors.get(genre, '03b2f8')
        emoji = genre_emojis.get(genre, '🎬')
        
        description = f"{emoji} 新しい動画をYouTubeに投稿しました!"
        
        fields = [
            {
                'name': '📺 動画タイトル',
                'value': title,
                'inline': False
            },
            {
                'name': '🎭 ジャンル',
                'value': genre.capitalize(),
                'inline': True
            },
            {
                'name': '🔗 URL',
                'value': f"[動画を見る]({video_url})",
                'inline': True
            }
        ]
        
        return self.send_notification(
            title="✅ YouTube動画アップロード完了",
            description=description,
            color=color,
            fields=fields,
            thumbnail_url=thumbnail_url
        )
    
    def notify_error(
        self,
        error_message: str,
        genre: Optional[str] = None
    ) -> bool:
        """
        エラーを通知
        
        Args:
            error_message: エラーメッセージ
            genre: ジャンル (オプション)
            
        Returns:
            送信成功かどうか
        """
        description = f"⚠️ 動画生成・アップロード中にエラーが発生しました"
        
        fields = [
            {
                'name': '❌ エラー内容',
                'value': error_message,
                'inline': False
            }
        ]
        
        if genre:
            fields.append({
                'name': '🎭 ジャンル',
                'value': genre.capitalize(),
                'inline': True
            })
        
        return self.send_notification(
            title="❌ エラー発生",
            description=description,
            color='FF0000',  # 赤
            fields=fields
        )


if __name__ == "__main__":
    # テスト実行
    import sys
    
    notifier = DiscordNotifier()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'success':
            notifier.notify_upload_success(
                video_url="https://www.youtube.com/watch?v=test",
                title="テスト動画",
                genre="horror"
            )
        elif sys.argv[1] == 'error':
            notifier.notify_error(
                error_message="テストエラーメッセージ",
                genre="trivia"
            )
    else:
        notifier.send_notification(
            title="テスト通知",
            description="これはテスト通知です"
        )
