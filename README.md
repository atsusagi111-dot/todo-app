# Todoリストアプリ

Flask + Google Sheets APIで作るシンプルなTodoリストWebアプリです。

## できること

- Todo一覧の表示
- Todoの登録（タイトル・内容・期日）
- Todoの編集
- Todoの完了チェック（チェックすると傍線＋グレーアウト＋「完了」表示、ポップアニメーション）
- 期日当日の朝7時（日本時間）にDiscordへ通知
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

## Discord通知（期日当日の朝7時）

`notify_discord.py` を実行すると、期日が今日で未完了のTodoについて、Discordの指定チャンネルへ「おはようございます。本日Todoリスト○○の実行日です🐇」と通知します。

```
python notify_discord.py
```

### Renderで毎朝7時（日本時間）に自動実行する設定

RenderのWebサービスは無料プランだと常時起動していないため、別途「Cron Job」サービスを作成して定期実行します。

1. Renderのダッシュボードで「New +」→「Cron Job」を選択
2. このリポジトリを接続
3. 以下を設定
   ```
   Build Command: pip install -r requirements.txt
   Command:       python notify_discord.py
   Schedule:      0 22 * * *
   ```
   （Renderのスケジュールは協定世界時(UTC)基準のため、日本時間7:00 = UTC 22:00 で `0 22 * * *` と指定する）
4. 環境変数に、Webサービスと同じ `GOOGLE_SERVICE_ACCOUNT_JSON` と `SPREADSHEET_ID`、加えて `DISCORD_WEBHOOK_URL` を設定する

## 技術構成

- Python / Flask
- Google Sheets API（gspread）
- Discord Webhook
- GitHub / Render

## 注意

`.env` とサービスアカウントのJSONキーファイルには秘密情報が含まれるため、`.gitignore`で除外しGitHubには含めていません。
