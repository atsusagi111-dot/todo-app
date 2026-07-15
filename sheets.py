# Googleスプレッドシートとのやり取りをまとめたファイル
# app.py からはここに定義した関数を呼び出すだけでよい

import json
import os

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# .env ファイルの内容を読み込む
load_dotenv()

# このファイルが置かれているフォルダ（JSONキーの場所を組み立てるために使う）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# スプレッドシート操作に必要な権限の範囲
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# シートの1行目（見出し行）
HEADER = ["id", "title", "content", "due", "done"]

# 初回セットアップ時に入れておくサンプルデータ
SEED_TODOS = [
    [1, "買い物に行く", "牛乳とパンを買う", "2026-07-12", "FALSE"],
    [2, "レポート提出", "Web開発実践課題のレポートをまとめる", "2026-07-15", "FALSE"],
    [3, "掃除する", "部屋とキッチンを掃除する", "2026-07-13", "FALSE"],
]

# 完了状態を表す文字列とみなす値
_TRUE_VALUES = {"TRUE", "1", "DONE"}


def _get_credentials():
    # Render等の本番環境では、JSONファイルの代わりに
    # 環境変数 GOOGLE_SERVICE_ACCOUNT_JSON にJSONの中身をそのまま設定する運用にする
    cred_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if cred_json:
        return Credentials.from_service_account_info(json.loads(cred_json), scopes=SCOPES)

    # ローカル開発では .env で指定したJSONファイルを読み込む
    cred_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    cred_path = os.path.join(BASE_DIR, cred_file)
    return Credentials.from_service_account_file(cred_path, scopes=SCOPES)


def _get_worksheet():
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    creds = _get_credentials()
    client = gspread.authorize(creds)
    worksheet = client.open_by_key(spreadsheet_id).sheet1

    # 見出し行がまだ無ければ作成し、サンプルデータを入れておく
    header_row = worksheet.row_values(1)
    if not header_row or header_row[0] != "id":
        worksheet.update("A1:E1", [HEADER])
        worksheet.append_rows(SEED_TODOS)
    elif "done" not in header_row:
        # 既存のシートに「done」列がまだ無い場合は見出しだけ追加する
        worksheet.update_acell("E1", "done")

    return worksheet


def get_all_todos():
    # シートの全データをTodoのリスト（辞書のリスト）として返す
    worksheet = _get_worksheet()
    records = worksheet.get_all_records()
    return [
        {
            "id": int(record["id"]),
            "title": record["title"],
            "content": record["content"],
            "due": str(record["due"]),
            "done": str(record.get("done", "")).strip().upper() in _TRUE_VALUES,
        }
        for record in records
    ]


def find_todo(todo_id):
    # 指定したidのTodoを1件だけ返す（見つからなければNone）
    for todo in get_all_todos():
        if todo["id"] == todo_id:
            return todo
    return None


def add_todo(title, content, due):
    # 新しいTodoを1行追加する（idは今ある最大値+1を自動で割り当てる）
    worksheet = _get_worksheet()
    todos = get_all_todos()
    next_id = max([todo["id"] for todo in todos], default=0) + 1
    worksheet.append_row([next_id, title, content, due, "FALSE"])


def update_todo(todo_id, title, content, due):
    # 指定したidの行を新しい内容で上書きする
    worksheet = _get_worksheet()
    cell = worksheet.find(str(todo_id), in_column=1)
    if cell is None:
        return False
    worksheet.update(f"A{cell.row}:D{cell.row}", [[todo_id, title, content, due]])
    return True


def toggle_todo(todo_id):
    # 指定したidの完了状態（done）を反転させる。戻り値は反転後の状態
    worksheet = _get_worksheet()
    cell = worksheet.find(str(todo_id), in_column=1)
    if cell is None:
        return None

    current = str(worksheet.cell(cell.row, 5).value or "").strip().upper() in _TRUE_VALUES
    new_done = not current
    worksheet.update_acell(f"E{cell.row}", "TRUE" if new_done else "FALSE")
    return new_done
