# デイリー通知 (AIニュース / Zenn AI関連人気記事)

毎日 7:00 (JST) に GitHub Actions が情報を取得し、このリポジトリに Issue を作成します。
作成された Issue はリポジトリオーナーにアサインされるため、GitHub の通知メールが自動的に届きます
(追加の SMTP/API キーの設定は不要です)。

## AI最新ニュース

- `.github/workflows/daily-ai-news.yml`: 毎日 22:00 UTC (07:00 JST) に実行されるスケジュールワークフロー。
  `workflow_dispatch` で手動実行も可能です。
- `scripts/fetch_ai_news.py`: Google News RSS (`q=AI`, 日本語/日本地域) から記事を取得し、
  直近24時間以内 (`MAX_AGE_HOURS`) の記事を新しい順に最大20件 (`MAX_ITEMS`) まで、
  Markdown 形式のニュース一覧として標準出力に出力します。

## Zenn AI関連人気記事

- `.github/workflows/daily-zenn-ai-articles.yml`: 毎日 22:00 UTC (07:00 JST) に実行されるスケジュールワークフロー。
  `workflow_dispatch` で手動実行も可能です。
- `scripts/fetch_zenn_ai_articles.py`: Zenn の公開 API からAI関連トピック
  (`ai`, `llm`, `生成ai`, `machinelearning` など、スクリプト内 `TOPICS` で変更可能) の
  新着記事を取得し、直近 7 日以内 (`MAX_AGE_DAYS`) に公開されたものへ絞り込んだうえで
  重複排除し、いいね数順に最大20件 (`MAX_ITEMS`) を Markdown 形式の記事一覧として
  標準出力に出力します（「最近公開された中で人気の記事」を配信します）。

## 通知を受け取るには

GitHub の通知設定 (Settings > Notifications) でメール通知が有効になっていれば、
Issue がアサインされた時点で自動的にメールが届きます。
