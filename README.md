# Slack Notice

Pythonコードの任意の場所からSlackへ通知を送信できるシンプルなモジュールです。

## 特徴

- **シンプル**: `notify("メッセージ")` の1行で通知
- **依存関係ゼロ**: Python標準ライブラリのみ使用
- **簡単セットアップ**: 環境変数1つで完了

## セットアップ

### 1. Webhook URLの取得

1. https://slack.com/services/new/incoming-webhook を開く
2. ワークスペースを選択してサインイン
3. 通知を送信するチャンネルを選択
4. **Incoming Webhook インテグレーションの追加** をクリック
5. 表示された **Webhook URL** をコピー

### 2. インストール

```bash
cd /path/to/slackNotice
pip install -e .
```

**Mac (Homebrew) の場合**:
```bash
pip install --user --break-system-packages -e .
```

### 3. 環境変数の設定

`.bashrc` または `.zshrc` に以下を追加：

```bash
export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'
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

### `SlackNotifier(bot_token=None, channel=None, webhook_url=None, load_env=True)`

トークン等を明示的に渡して使うクラスです。省略した項目は環境変数（利用側プロジェクトの `.env` を含む）から補完されます。
`notify()` / `send_csv()` は、このクラスのメソッドを呼ぶショートカットです。

```python
from slack_notice import SlackNotifier

slack = SlackNotifier(bot_token="xoxb-...", channel="C0123456789")
slack.send_csv("result.csv", message="集計結果です")
```

### `send_csv(file_path, channel=None, message=None, title=None)`

CSVファイルをSlackにアップロードします。Webhookではファイルを送れないため、
Botトークン（`files:write` スコープ）が必要です。Botは送信先チャンネルに招待してください。

```bash
export SLACK_BOT_TOKEN='xoxb-...'
export SLACK_CHANNEL_ID='C0123456789'   # 送信先チャンネルID
```

```python
from slack_notice import send_csv
send_csv("result.csv", message="集計結果です")
```

```bash
python slack_notice.py --csv result.csv "集計結果です"
```

## 動作環境

- Python 3.6以上
- 外部ライブラリ不要

## ライセンス

MIT License
