# 期日当日の朝にDiscordへ通知を送るスクリプト
# RenderのCron Jobから「python notify_discord.py」として1日1回実行される想定

import os
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

import sheets

load_dotenv()

# 日本時間（UTC+9固定。日本にサマータイムは無いため固定オフセットで問題ない）
JST = timezone(timedelta(hours=9))


def send_due_today_notifications():
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL が設定されていないため、通知をスキップしました。")
        return

    today = datetime.now(JST).strftime("%Y-%m-%d")
    todos = sheets.get_all_todos()

    # 期日が今日で、まだ完了していないTodoだけを通知対象にする
    due_today = [todo for todo in todos if todo["due"] == today and not todo["done"]]

    for todo in due_today:
        message = f"おはようございます。本日Todoリスト{todo['title']}の実行日です🐇"
        response = requests.post(webhook_url, json={"content": message}, timeout=10)
        response.raise_for_status()
        print(f"通知を送信しました: {todo['title']}")

    if not due_today:
        print("本日期日のTodoはありませんでした。")


if __name__ == "__main__":
    send_due_today_notifications()
