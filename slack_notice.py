#!/usr/bin/env python3
"""
Slack通知モジュール

任意のPythonコードからSlackへ簡単に通知を送信できます。

使用例:
    from slack_notice import notify
    notify("処理が完了しました")

    from slack_notice import SlackNotifier
    slack = SlackNotifier(bot_token="xoxb-...", channel="C0123456789")
    slack.send_csv("result.csv")
"""

import json
import os
import urllib.parse
import urllib.request
import urllib.error
from typing import Optional


# 環境変数名
ENV_WEBHOOK_URL = "SLACK_WEBHOOK_URL"
ENV_BOT_TOKEN = "SLACK_BOT_TOKEN"
ENV_CHANNEL_ID = "SLACK_CHANNEL_ID"


def _find_dotenv() -> Optional[str]:
    """カレントディレクトリから親ディレクトリへ遡り、最初に見つかった .env のパスを返す"""
    directory = os.getcwd()
    while True:
        path = os.path.join(directory, ".env")
        if os.path.isfile(path):
            return path
        parent = os.path.dirname(directory)
        if parent == directory:
            return None
        directory = parent


def _load_dotenv() -> None:
    """利用側プロジェクトの .env を読み込む（既存の環境変数は上書きしない）"""
    path = _find_dotenv()
    if not path:
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key.startswith("export "):
                key = key[len("export "):].strip()
            os.environ.setdefault(key, value.strip().strip("'\""))


class SlackNoticeError(Exception):
    """Slack通知関連のエラー"""
    pass


def _slack_api(method: str, token: str, *, form: Optional[dict] = None, body: Optional[dict] = None) -> dict:
    """Slack Web APIを呼び出し、レスポンスのJSONを返す"""
    url = f"https://slack.com/api/{method}"
    headers = {"Authorization": f"Bearer {token}"}

    if form is not None:
        data = urllib.parse.urlencode(form).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    else:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"

    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SlackNoticeError(f"Slack API エラー: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise SlackNoticeError(f"接続エラー: {e.reason}")

    if not result.get("ok"):
        raise SlackNoticeError(f"Slack API エラー ({method}): {result.get('error')}")
    return result


class SlackNotifier:
    """
    Slack通知クライアント

    引数を省略した項目は、環境変数（利用側プロジェクトの .env を含む）から補完します。

    Args:
        bot_token: Botトークン（xoxb-...）。CSV送信に必要
        channel: 送信先チャンネルID。CSV送信に必要
        webhook_url: Incoming Webhook URL。テキスト通知に必要
        load_env: Trueなら不足分を環境変数 / .env から補完する

    Example:
        >>> slack = SlackNotifier(bot_token="xoxb-...", channel="C0123456789")
        >>> slack.send_csv("result.csv", message="集計結果です")
        True
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        channel: Optional[str] = None,
        webhook_url: Optional[str] = None,
        load_env: bool = True,
    ):
        if load_env and not (bot_token and channel and webhook_url):
            _load_dotenv()
            bot_token = bot_token or os.environ.get(ENV_BOT_TOKEN)
            channel = channel or os.environ.get(ENV_CHANNEL_ID)
            webhook_url = webhook_url or os.environ.get(ENV_WEBHOOK_URL)

        self.bot_token = bot_token
        self.channel = channel
        self.webhook_url = webhook_url

    def notify(
        self,
        message: str,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
    ) -> bool:
        """
        Webhook経由でテキストを通知する

        Args:
            message: 送信するメッセージ
            channel: 送信先チャンネル（省略時はWebhookのデフォルト）
            username: 表示名（省略時はWebhookのデフォルト）
            icon_emoji: アイコン絵文字（例: ":robot_face:"）

        Returns:
            bool: 送信成功時True

        Raises:
            SlackNoticeError: 設定エラーまたは送信エラー時
        """
        if not self.webhook_url:
            raise SlackNoticeError(
                f"Webhook URLが未設定です。webhook_url 引数または環境変数 {ENV_WEBHOOK_URL} で指定してください。"
            )

        payload = {"text": message}
        if channel:
            payload["channel"] = channel
        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji

        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(self.webhook_url, data=data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.status == 200
        except urllib.error.HTTPError as e:
            raise SlackNoticeError(f"Slack API エラー: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise SlackNoticeError(f"接続エラー: {e.reason}")

    def send_csv(
        self,
        file_path: str,
        channel: Optional[str] = None,
        message: Optional[str] = None,
        title: Optional[str] = None,
    ) -> bool:
        """
        CSVファイルをSlackに送信する

        Botトークン(files:write スコープ)が必要です。Botは送信先チャンネルに招待されている必要があります。

        Args:
            file_path: 送信するCSVファイルのパス
            channel: 送信先チャンネルID（省略時はインスタンスの channel）
            message: ファイルに添えるコメント
            title: Slack上のファイルタイトル（省略時はファイル名）

        Returns:
            bool: 送信成功時True

        Raises:
            SlackNoticeError: 設定エラーまたは送信エラー時
        """
        token = self.bot_token
        if not token:
            raise SlackNoticeError(
                f"Botトークンが未設定です。bot_token 引数または環境変数 {ENV_BOT_TOKEN} で指定してください。"
            )

        channel = channel or self.channel
        if not channel:
            raise SlackNoticeError(
                f"送信先チャンネルIDが未設定です。channel 引数または環境変数 {ENV_CHANNEL_ID} で指定してください。"
            )

        try:
            with open(file_path, "rb") as f:
                content = f.read()
        except OSError as e:
            raise SlackNoticeError(f"ファイルを読み込めません: {e}")

        filename = os.path.basename(file_path)

        # 1. アップロードURLの取得
        upload = _slack_api(
            "files.getUploadURLExternal",
            token,
            form={"filename": filename, "length": len(content)},
        )

        # 2. ファイル本体のアップロード
        req = urllib.request.Request(
            upload["upload_url"],
            data=content,
            headers={"Content-Type": "text/csv"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60):
                pass
        except urllib.error.HTTPError as e:
            raise SlackNoticeError(f"アップロードエラー: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise SlackNoticeError(f"接続エラー: {e.reason}")

        # 3. アップロード完了・チャンネルへ共有
        body = {
            "files": [{"id": upload["file_id"], "title": title or filename}],
            "channel_id": channel,
        }
        if message:
            body["initial_comment"] = message
        _slack_api("files.completeUploadExternal", token, body=body)
        return True


def notify(
    message: str,
    channel: Optional[str] = None,
    username: Optional[str] = None,
    icon_emoji: Optional[str] = None,
) -> bool:
    """Slackに通知を送信する（SlackNotifier().notify のショートカット）"""
    return SlackNotifier().notify(message, channel, username, icon_emoji)


def send_csv(
    file_path: str,
    channel: Optional[str] = None,
    message: Optional[str] = None,
    title: Optional[str] = None,
) -> bool:
    """CSVをSlackに送信する（SlackNotifier().send_csv のショートカット）"""
    return SlackNotifier().send_csv(file_path, channel, message, title)


# 簡易エイリアス
send = notify


if __name__ == "__main__":
    # コマンドラインから直接実行時のテスト
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python slack_notice.py 'メッセージ'")
        print("          python slack_notice.py --csv ファイル.csv ['コメント']")
        sys.exit(1)

    try:
        if sys.argv[1] == "--csv":
            if len(sys.argv) < 3:
                print("CSVファイルのパスを指定してください", file=sys.stderr)
                sys.exit(1)
            send_csv(sys.argv[2], message=sys.argv[3] if len(sys.argv) > 3 else None)
            print("CSVを送信しました")
        else:
            notify(sys.argv[1])
            print("通知を送信しました")
    except SlackNoticeError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

