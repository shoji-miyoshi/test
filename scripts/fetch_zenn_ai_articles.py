#!/usr/bin/env python3
"""Fetch recent popular AI-related Zenn articles and print a Markdown summary."""
import datetime
import json
import sys
import urllib.parse
import urllib.request

API_URL = "https://zenn.dev/api/articles"
TOPICS = [
    "ai",
    "llm",
    "生成ai",
    "machinelearning",
    "deeplearning",
    "chatgpt",
    "claude",
    "openai",
]
MAX_ITEMS = 20
MAX_AGE_DAYS = 7
FETCH_COUNT = 48


def fetch_topic_articles(topic: str) -> list:
    query = urllib.parse.urlencode(
        {"topicname": topic, "order": "latest", "count": FETCH_COUNT}
    )
    req = urllib.request.Request(
        f"{API_URL}?{query}", headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read()).get("articles", [])


def is_recent(article: dict, cutoff: datetime.datetime) -> bool:
    published = article.get("published_at")
    if not published:
        return False
    try:
        pub_dt = datetime.datetime.fromisoformat(published)
    except ValueError:
        return False
    if pub_dt.tzinfo is None:
        pub_dt = pub_dt.replace(tzinfo=datetime.timezone.utc)
    return pub_dt >= cutoff


def collect_articles() -> list:
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=MAX_AGE_DAYS
    )
    seen = set()
    articles = []
    for topic in TOPICS:
        try:
            topic_articles = fetch_topic_articles(topic)
        except Exception as exc:  # a single topic failing shouldn't kill the digest
            print(f"warning: failed to fetch topic {topic!r}: {exc}", file=sys.stderr)
            continue
        for article in topic_articles:
            key = article.get("id") or article.get("path")
            if key is None or key in seen:
                continue
            if not is_recent(article, cutoff):
                continue
            seen.add(key)
            articles.append(article)
    articles.sort(key=lambda a: a.get("liked_count") or 0, reverse=True)
    return articles[:MAX_ITEMS]


def build_markdown(articles: list) -> str:
    if not articles:
        return f"直近{MAX_AGE_DAYS}日以内のAI関連人気記事は見つかりませんでした。"

    lines = []
    for article in articles:
        title = (article.get("title") or "").strip()
        path = article.get("path") or ""
        liked = article.get("liked_count") or 0
        author = (article.get("user") or {}).get("name") or ""
        published = (article.get("published_at") or "")[:10]
        lines.append(f"- [{title}](https://zenn.dev{path})  \n  ♥ {liked} / {author} / {published}")
    return "\n".join(lines)


def main() -> int:
    today = datetime.date.today().isoformat()
    try:
        body = build_markdown(collect_articles())
    except Exception as exc:  # network or parse failure shouldn't crash the workflow
        body = f"記事の取得中にエラーが発生しました: {exc}"

    print(f"## {today} の Zenn AI関連人気記事（直近{MAX_AGE_DAYS}日）\n")
    print(body)
    print("\n---\n出典: [Zenn](https://zenn.dev/topics/ai) のAI関連トピック (直近の新着をいいね数順)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
