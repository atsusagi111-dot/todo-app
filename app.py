# Flaskアプリの本体ファイル
# ここにルーティング（URLとページの対応）を書いていく

from flask import Flask, render_template, request, redirect, url_for, abort, jsonify

import sheets

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
