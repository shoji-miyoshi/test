# デイリー通知 (AIニュース / Zenn AI関連人気記事)

毎日 7:00 (JST) に GitHub Actions が情報を取得し、このリポジトリに Issue を作成します。
作成された Issue はリポジトリオーナーにアサインされるため、GitHub の通知メールが自動的に届きます
(追加の SMTP/API キーの設定は不要です)。

## AI最新ニュース

- `.github/workflows/daily-ai-news.yml`: 毎日 22:00 UTC (07:00 JST) に実行されるスケジュールワークフロー。
  `workflow_dispatch` で手動実行も可能です。
- `scripts/fetch_ai_news.py`: Google News RSS から、国内 (`hl=ja&gl=JP&ceid=JP:ja`) と
  海外 (`hl=en-US&gl=US&ceid=US:en`) の2つのフィードで記事を取得し、
  直近24時間以内 (`MAX_AGE_HOURS`) の記事を新しい順に各最大15件 (`MAX_ITEMS`) まで、
  「🇯🇵 国内ニュース」「🌍 海外ニュース（日本語訳）」に分けて Markdown 形式で標準出力に出力します。
  海外ニュースのタイトルは、非公式（APIキー不要）の Google 翻訳エンドポイント
  (`translate.googleapis.com`) で日本語に翻訳し、元の英語タイトルも「原題:」として併記します。
  翻訳に失敗した場合は原文のまま表示されます。
  なお Google News RSS は記事の要約テキストを提供しないため、翻訳対象はタイトルのみです。

## Zenn AI関連人気記事

- `.github/workflows/daily-zenn-ai-articles.yml`: 毎日 22:00 UTC (07:00 JST) に実行されるスケジュールワークフロー。
  `workflow_dispatch` で手動実行も可能です。
- `scripts/fetch_zenn_ai_articles.py`: Zenn の公開 API からAI関連トピック
  (`ai`, `llm`, `生成ai`, `machinelearning` など、スクリプト内 `TOPICS` で変更可能) の
  記事を新着順 (`order=latest`) にまとめて取得し、以下の 2 セクションに分けて
  Markdown 形式で標準出力に出力します。
  - **🆕 新着**: 直近 7 日 (`MAX_AGE_DAYS_NEW`) に公開され、いいねが 3 以上 (`MIN_LIKES_NEW`) 付いた
    記事を、公開日の新しい順で最大 20 件 (`MAX_ITEMS_NEW`)。投稿直後で反応のない記事は除外します。
  - **🔥 人気**: 直近 30 日 (`MAX_AGE_DAYS_POPULAR`) に公開された記事を、いいね数の多い順で
    最大 10 件 (`MAX_ITEMS_POPULAR`)。期間を区切っているため日々入れ替わります。

## 通知を受け取るには

GitHub の通知設定 (Settings > Notifications) でメール通知が有効になっていれば、
Issue がアサインされた時点で自動的にメールが届きます。
