# 期日当日の朝、および期日前日の夜にDiscordへ通知を送るスクリプト
# GitHub Actions（.github/workflows/notify-discord.yml）から
#   python notify_discord.py today    … 期日当日の朝
#   python notify_discord.py tomorrow … 期日前日の夜21:00
# としてそれぞれ1日1回実行される想定

import os
import sys
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

import sheets

load_dotenv()

# 日本時間（UTC+9固定。日本にサマータイムは無いため固定オフセットで問題ない）
JST = timezone(timedelta(hours=9))


def _send_notifications(target_date, due_todos, message_builder):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL が設定されていないため、通知をスキップしました。")
        return

    for todo in due_todos:
        message = message_builder(todo)
        response = requests.post(webhook_url, json={"content": message}, timeout=10)
        response.raise_for_status()
        print(f"通知を送信しました: {todo['title']}")

    if not due_todos:
        print(f"{target_date} が期日のTodoはありませんでした。")


def send_due_today_notifications():
    today = datetime.now(JST).strftime("%Y-%m-%d")
    todos = sheets.get_all_todos()

    # 期日が今日で、まだ完了していないTodoだけを通知対象にする
    due_today = [todo for todo in todos if todo["due"] == today and not todo["done"]]

    _send_notifications(
        today,
        due_today,
        lambda todo: f"おはようございます。本日Todoリスト{todo['title']}の実行日です🐇",
    )


def send_due_tomorrow_notifications():
    tomorrow = (datetime.now(JST) + timedelta(days=1)).strftime("%Y-%m-%d")
    todos = sheets.get_all_todos()

    # 期日が明日で、まだ完了していないTodoだけを通知対象にする
    due_tomorrow = [todo for todo in todos if todo["due"] == tomorrow and not todo["done"]]

    _send_notifications(
        tomorrow,
        due_tomorrow,
        lambda todo: f"こんばんは。明日はTodoリスト「{todo['title']}」の期日です🐇 準備を忘れずに！",
    )


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "today"
    if mode == "tomorrow":
        send_due_tomorrow_notifications()
    elif mode == "today":
        send_due_today_notifications()
    else:
        print(f"不明なモードです: {mode}（today または tomorrow を指定してください）")
        sys.exit(1)
