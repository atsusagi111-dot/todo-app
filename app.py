# Flaskアプリの本体ファイル
# ここにルーティング（URLとページの対応）を書いていく

import calendar as calendar_module
from datetime import date, datetime, timedelta, timezone

from flask import Flask, render_template, request, redirect, url_for, abort, jsonify

import sheets

# 日本時間（UTC+9固定。日本にサマータイムは無いため固定オフセットで問題ない）
JST = timezone(timedelta(hours=9))

# カレンダーの曜日見出し（日曜始まり）
WEEKDAY_LABELS = ["日", "月", "火", "水", "木", "金", "土"]

# Flaskアプリを作成
app = Flask(__name__)


# トップページ（"/"）にアクセスしたときの処理
@app.route("/")
def index():
    # スプレッドシートからTodo一覧を取得して表示する
    todos = sheets.get_all_todos()
    return render_template("index.html", todos=todos)


# Todo登録ページ（"/add"）
# GET: 登録フォームを表示する / POST: フォームの内容をスプレッドシートに追加する
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # フォームから送られてきた値を取得する
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        due = request.form.get("due", "").strip()

        # タイトルが空でなければ登録する
        if title:
            sheets.add_todo(title, content, due)

        # 登録後はトップページに戻る
        return redirect(url_for("index"))

    # GETのときはフォーム画面を表示する
    return render_template("add.html")


# Todo編集ページ（"/edit/<id>"）
# GET: 既存の内容を入れたフォームを表示する / POST: 内容を書き換える
@app.route("/edit/<int:todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    todo = sheets.find_todo(todo_id)

    # 指定されたidのTodoが存在しない場合は404エラーにする
    if todo is None:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        due = request.form.get("due", "").strip()

        # タイトルが空でなければ更新する
        if title:
            sheets.update_todo(todo_id, title, content, due)

        return redirect(url_for("index"))

    # GETのときは今の内容を入れたフォーム画面を表示する
    return render_template("edit.html", todo=todo)


# カレンダーページ（"/calendar"）。日付ごとのTodoを月表示する
@app.route("/calendar")
def calendar_view():
    today = datetime.now(JST).date()

    # 表示する年月（指定が無ければ今月）。
    # month=13やmonth=0のような範囲外の値が来ても正しい年月に正規化する
    year = request.args.get("year", type=int, default=today.year)
    month = request.args.get("month", type=int, default=today.month)
    month_index = year * 12 + (month - 1)
    year, month = divmod(month_index, 12)
    month += 1
    first_day = date(year, month, 1)

    # 日曜始まりで、その月を含む週すべての日付を取得する（前後月の日付を含む）
    cal = calendar_module.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)

    # Todoを期日ごとにまとめておく
    todos_by_date = {}
    for todo in sheets.get_all_todos():
        todos_by_date.setdefault(todo["due"], []).append(todo)

    prev_first = first_day - timedelta(days=1)
    next_first = (first_day + timedelta(days=32)).replace(day=1)

    return render_template(
        "calendar.html",
        weeks=weeks,
        weekday_labels=WEEKDAY_LABELS,
        year=year,
        month=month,
        today=today,
        todos_by_date=todos_by_date,
        prev_year=prev_first.year,
        prev_month=prev_first.month,
        next_year=next_first.year,
        next_month=next_first.month,
    )


# Todoの完了状態を切り替えるAPI（一覧の☑をクリックしたときにJSから呼ばれる）
@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    new_done = sheets.toggle_todo(todo_id)

    # 指定されたidのTodoが存在しない場合は404エラーにする
    if new_done is None:
        abort(404)

    return jsonify(done=new_done)


# このファイルを直接実行したときだけサーバーを起動する
if __name__ == "__main__":
    app.run(debug=True)
