#!/usr/bin/env python3
"""Fetch the latest AI news from Google News RSS and print a Markdown summary."""
import datetime
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED_URL = "https://news.google.com/rss/search?q=AI&hl=ja&gl=JP&ceid=JP:ja"
MAX_ITEMS = 20
MAX_AGE_HOURS = 24


def fetch_feed(url: str) -> ET.Element:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return ET.fromstring(response.read())


def build_markdown(root: ET.Element) -> str:
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=MAX_AGE_HOURS)
    items = []
    for item in root.findall("./channel/item"):
        pub_date = (item.findtext("pubDate") or "").strip()
        try:
            pub_dt = parsedate_to_datetime(pub_date)
        except (TypeError, ValueError):
            continue
        if pub_dt < cutoff:
            continue
        items.append((pub_dt, item, pub_date))
    items.sort(key=lambda t: t[0], reverse=True)
    items = items[:MAX_ITEMS]

    if not items:
        return f"直近{MAX_AGE_HOURS}時間以内のニュースは見つかりませんでした。"

    lines = []
    for _, item, pub_date in items:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
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
