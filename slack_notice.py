#!/usr/bin/env python3
"""
Slack通知モジュール

任意のPythonコードからSlackへ簡単に通知を送信できます。

使用例:
    from slack_notice import notify
    notify("処理が完了しました")
"""

import json
import os
import urllib.request
import urllib.error
from typing import Optional


# 環境変数名
ENV_WEBHOOK_URL = "SLACK_WEBHOOK_URL"


class SlackNoticeError(Exception):
    """Slack通知関連のエラー"""
    pass


def _get_webhook_url() -> str:
    """環境変数からWebhook URLを取得"""
    webhook_url = os.environ.get(ENV_WEBHOOK_URL)
    
    if not webhook_url:
        raise SlackNoticeError(
            f"環境変数 {ENV_WEBHOOK_URL} が設定されていません。\n"
            f"以下のコマンドで設定してください:\n"
            f"  export {ENV_WEBHOOK_URL}='https://hooks.slack.com/services/...'"
        )
    
    return webhook_url


def notify(
    message: str,
    channel: Optional[str] = None,
    username: Optional[str] = None,
    icon_emoji: Optional[str] = None,
) -> bool:
    """
    Slackに通知を送信する

    Args:
        message: 送信するメッセージ
        channel: 送信先チャンネル（省略時はWebhookのデフォルト）
        username: 表示名（省略時はWebhookのデフォルト）
        icon_emoji: アイコン絵文字（例: ":robot_face:"）

    Returns:
        bool: 送信成功時True

    Raises:
        SlackNoticeError: 設定エラーまたは送信エラー時

    Example:
        >>> notify("処理が完了しました")
        True
        >>> notify("エラー発生", channel="#alerts", icon_emoji=":warning:")
        True
    """
    webhook_url = _get_webhook_url()
    
    # ペイロード作成
    payload = {"text": message}
    
    if channel:
        payload["channel"] = channel
    if username:
        payload["username"] = username
    if icon_emoji:
        payload["icon_emoji"] = icon_emoji
    
    # リクエスト送信
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    
    req = urllib.request.Request(webhook_url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status == 200
    except urllib.error.HTTPError as e:
        raise SlackNoticeError(f"Slack API エラー: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise SlackNoticeError(f"接続エラー: {e.reason}")


# 簡易エイリアス
send = notify


if __name__ == "__main__":
    # コマンドラインから直接実行時のテスト
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python slack_notice.py 'メッセージ'")
        sys.exit(1)
    
    try:
        notify(sys.argv[1])
        print("通知を送信しました")
    except SlackNoticeError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

