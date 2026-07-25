#!/usr/bin/env python3
"""Fetch Zenn AI articles as a two-section digest: newest and most-liked."""
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
MAX_ITEMS_NEW = 10
MAX_ITEMS_POPULAR = 10
FETCH_COUNT = 48


def fetch_topic_articles(topic: str, order: str) -> list:
    query = urllib.parse.urlencode(
        {"topicname": topic, "order": order, "count": FETCH_COUNT}
    )
    req = urllib.request.Request(
        f"{API_URL}?{query}", headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read()).get("articles", [])


def collect(order: str) -> list:
    """Fetch and de-duplicate articles across all topics for a given ordering."""
    seen = set()
    articles = []
    for topic in TOPICS:
        try:
            topic_articles = fetch_topic_articles(topic, order)
        except Exception as exc:  # a single topic failing shouldn't kill the digest
            print(
                f"warning: failed to fetch topic {topic!r} ({order}): {exc}",
                file=sys.stderr,
            )
            continue
        for article in topic_articles:
            key = article.get("id") or article.get("path")
            if key is None or key in seen:
                continue
            seen.add(key)
            articles.append(article)
    return articles


def parse_published(article: dict):
    published = article.get("published_at")
    if not published:
        return None
    try:
        dt = datetime.datetime.fromisoformat(published)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def top_newest(articles: list, limit: int) -> list:
    dated = [(parse_published(a), a) for a in articles]
    dated = [(d, a) for d, a in dated if d is not None]
    dated.sort(key=lambda t: t[0], reverse=True)
    return [a for _, a in dated[:limit]]


def top_liked(articles: list, limit: int) -> list:
    return sorted(articles, key=lambda a: a.get("liked_count") or 0, reverse=True)[:limit]


def format_lines(articles: list, empty_msg: str) -> str:
    if not articles:
        return empty_msg
    lines = []
    for article in articles:
        title = (article.get("title") or "").strip()
        path = article.get("path") or ""
        liked = article.get("liked_count") or 0
        author = (article.get("user") or {}).get("name") or ""
        published = (article.get("published_at") or "")[:10]
        lines.append(f"- [{title}](https://zenn.dev{path})  \n  ♥ {liked} / {author} / {published}")
    return "\n".join(lines)


def build_body() -> str:
    newest = top_newest(collect("latest"), MAX_ITEMS_NEW)
    popular = top_liked(collect("daily"), MAX_ITEMS_POPULAR)
    new_section = format_lines(newest, "新着記事は見つかりませんでした。")
    popular_section = format_lines(popular, "人気記事は見つかりませんでした。")
    return (
        f"### 🆕 新着（公開日の新しい順）\n\n{new_section}\n\n"
        f"### 🔥 人気（いいね数の多い順）\n\n{popular_section}"
    )


def main() -> int:
    today = datetime.date.today().isoformat()
    try:
        body = build_body()
    except Exception as exc:  # network or parse failure shouldn't crash the workflow
        body = f"記事の取得中にエラーが発生しました: {exc}"

    print(f"## {today} の Zenn AI関連記事\n")
    print(body)
    print("\n---\n出典: [Zenn](https://zenn.dev/topics/ai) のAI関連トピック")
    return 0


if __name__ == "__main__":
    sys.exit(main())
