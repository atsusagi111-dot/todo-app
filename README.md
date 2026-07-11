# Todoリストアプリ

Flask + Google Sheets APIで作るシンプルなTodoリストWebアプリです。

## できること

- Todo一覧の表示
- Todoの登録（タイトル・内容・期日）
- Todoの編集
- データはGoogleスプレッドシートに保存

## セットアップ（ローカルで動かす場合）

1. 必要なライブラリをインストール
   ```
   pip install -r requirements.txt
   ```
2. Googleサービスアカウントを作成し、JSONキーを取得
3. Todoデータを保存したいGoogleスプレッドシートを作成し、サービスアカウントのメールアドレスを編集者として共有
4. プロジェクト直下に `.env` ファイルを作成し、以下を設定
   ```
   GOOGLE_SERVICE_ACCOUNT_FILE=サービスアカウントJSONファイル名.json
   SPREADSHEET_ID=スプレッドシートのID（URLの/d/と/editの間の文字列）
   ```
5. サービスアカウントのJSONキーファイルをプロジェクト直下に配置
6. サーバーを起動
   ```
   python app.py
   ```
7. ブラウザで `http://127.0.0.1:5000` にアクセス

## 技術構成

- Python / Flask
- Google Sheets API（gspread）
- GitHub / Render

## 注意

`.env` とサービスアカウントのJSONキーファイルには秘密情報が含まれるため、`.gitignore`で除外しGitHubには含めていません。
