#!/usr/bin/env python3
"""Fetch the latest AI news from Google News RSS and print a Markdown summary."""
import datetime
import sys
import urllib.request
import xml.etree.ElementTree as ET

FEED_URL = "https://news.google.com/rss/search?q=AI&hl=ja&gl=JP&ceid=JP:ja"
MAX_ITEMS = 10


def fetch_feed(url: str) -> ET.Element:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return ET.fromstring(response.read())


def build_markdown(root: ET.Element) -> str:
    items = root.findall("./channel/item")[:MAX_ITEMS]
    if not items:
        return "本日はニュースを取得できませんでした。"

    lines = []
    for item in items:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        source = item.findtext("source") or ""
        lines.append(f"- [{title}]({link})  \n  {source} / {pub_date}")
    return "\n".join(lines)


def main() -> int:
    today = datetime.date.today().isoformat()
    try:
        root = fetch_feed(FEED_URL)
        body = build_markdown(root)
    except Exception as exc:  # network or parse failure shouldn't crash the workflow
        body = f"ニュースの取得中にエラーが発生しました: {exc}"

    print(f"## {today} の AI最新ニュース\n")
    print(body)
    print(f"\n---\n出典: [Google News検索 \"AI\"](https://news.google.com/search?q=AI&hl=ja&gl=JP)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
