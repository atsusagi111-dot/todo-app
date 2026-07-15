# Todoリストアプリ

Flask + Google Sheets APIで作るシンプルなTodoリストWebアプリです。

## できること

- Todo一覧の表示
- Todoの登録（タイトル・内容・期日）
- Todoの編集
- Todoの完了チェック（チェックすると傍線＋グレーアウト＋「完了」表示、ポップアニメーション）
- 期日当日の朝7時（日本時間）にDiscordへ通知
- 期日前日の夜21時（日本時間）にDiscordへ通知
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
   DISCORD_WEBHOOK_URL=DiscordのWebhook URL（期日通知を送るチャンネルのもの）
   ```
5. サービスアカウントのJSONキーファイルをプロジェクト直下に配置
6. サーバーを起動
   ```
   python app.py
   ```
7. ブラウザで `http://127.0.0.1:5000` にアクセス

## Discord通知（期日当日の朝7時 / 前日の夜21時）

`notify_discord.py` はモード引数（`today` / `tomorrow`）を受け取り、Discordの指定チャンネルへ通知します。

- `python notify_discord.py today`（引数省略時のデフォルトも同じ）
  期日が今日で未完了のTodoについて「おはようございます。本日Todoリスト○○の実行日です🐇」と通知
- `python notify_discord.py tomorrow`
  期日が明日で未完了のTodoについて「こんばんは。明日はTodoリスト「○○」の期日です🐇 準備を忘れずに！」と通知

```
python notify_discord.py today
python notify_discord.py tomorrow
```

### GitHub Actionsで自動実行する設定（毎朝7時5分 / 前日夜21時5分、いずれも日本時間）

`.github/workflows/notify-discord.yml` が、GitHub Actionsのスケジュール実行（`schedule`トリガー）でこのスクリプトを定期実行します。Renderの無料プランのようなスリープが無いため、追加のサーバーやCron Jobサービスは不要です。

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」→「New repository secret」で、以下の3つを登録する
   ```
   GOOGLE_SERVICE_ACCOUNT_JSON … サービスアカウントJSONキーファイルの中身をそのまま貼り付け
   SPREADSHEET_ID              … スプレッドシートのID
   DISCORD_WEBHOOK_URL         … DiscordのWebhook URL
   ```
2. `main`（または既定ブランチ）にpushすると、GitHubが自動的にワークフローを認識する
3. スケジュールは以下の2本（UTC基準。GitHubの推奨に従い、混雑しやすい「毎時ちょうど」を避けて5分ずらしている）
   ```
   5 22 * * *  … 日本時間7:05（当日期日の朝通知）
   5 12 * * *  … 日本時間21:05（前日期日の夜通知）
   ```
4. 動作確認したいときは、GitHubリポジトリの「Actions」タブ→「Discord期日通知」→「Run workflow」から手動実行できる（`mode`で`today`/`tomorrow`を選択）

## 技術構成

- Python / Flask
- Google Sheets API（gspread）
- Discord Webhook
- GitHub / GitHub Actions / Render

## 注意

`.env` とサービスアカウントのJSONキーファイルには秘密情報が含まれるため、`.gitignore`で除外しGitHubには含めていません。
