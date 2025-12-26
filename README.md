# Slack Notice

Pythonコードの任意の場所からSlackへ通知を送信できるシンプルなモジュールです。

## 特徴

- **シンプル**: `notify("メッセージ")` の1行で通知
- **依存関係ゼロ**: Python標準ライブラリのみ使用
- **簡単セットアップ**: 環境変数1つで完了

## セットアップ

### 1. Webhook URLの取得

1. Slackワークスペースの **Incoming Webhook** 設定ページを開く
   - `https://<ワークスペース名>.slack.com/marketplace/new/A0F7XDUAZ--incoming-webhook-`
2. **Slackに追加** をクリック
3. 通知を送信するチャンネルを選択
4. **Incoming Webhook インテグレーションの追加** をクリック
5. 表示された **Webhook URL** をコピー

### 2. 環境変数の設定

`.bashrc` または `.zshrc` に以下を追加：

```bash
export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'
export PYTHONPATH="${PYTHONPATH}:/path/to/slackNotice"
```

設定を反映：

```bash
source ~/.bashrc  # または source ~/.zshrc
```

## 使用方法

```python
from slack_notice import notify

notify("処理が完了しました")
```

### オプション

```python
# チャンネル指定
notify("重要な通知", channel="#alerts")

# 表示名とアイコンを変更
notify("バッチ処理完了", username="BatchBot", icon_emoji=":robot_face:")
```

### コマンドラインから使用

```bash
python slack_notice.py "テスト通知"
```

## API

### `notify(message, channel=None, username=None, icon_emoji=None)`

| 引数 | 型 | 説明 |
|------|------|------|
| `message` | str | 送信するメッセージ（必須） |
| `channel` | str | 送信先チャンネル |
| `username` | str | 表示名 |
| `icon_emoji` | str | アイコン絵文字（例: `:bell:`） |

## 動作環境

- Python 3.6以上
- 外部ライブラリ不要

## ライセンス

MIT License
