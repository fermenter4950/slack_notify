#!/usr/bin/env python3
"""
Slack通知モジュールの使用例

実行前に ~/.slack_notice.json を設定してください。
"""

from slack_notice import notify, SlackNoticeError


def example_basic():
    """基本的な通知"""
    notify("Hello from Python!")


def example_with_options():
    """オプション付き通知"""
    notify(
        "カスタム通知のテスト",
        username="TestBot",
        icon_emoji=":tada:"
    )


def example_in_script():
    """スクリプト内での実践的な使用例"""
    print("重い処理を開始...")
    
    # 何か重い処理
    total = sum(range(1000000))
    
    # 処理完了を通知
    notify(f"処理完了: 合計値 = {total}")
    print("通知を送信しました")


def example_with_error_handling():
    """エラーハンドリング付き"""
    try:
        notify("エラーハンドリングのテスト")
        print("通知成功!")
    except SlackNoticeError as e:
        print(f"通知に失敗しました: {e}")


if __name__ == "__main__":
    print("=== Slack通知テスト ===\n")
    
    try:
        # 基本的な通知をテスト
        example_basic()
        print("基本的な通知: 成功")
        
    except SlackNoticeError as e:
        print(f"エラー: {e}")
        print("\n設定を確認してください:")
        print("1. ~/.slack_notice.json が存在するか")
        print("2. webhook_url が正しく設定されているか")

