#!/usr/bin/env python3
"""Fetch the latest domestic and overseas AI news from Google News RSS,
translate overseas headlines to Japanese, and print a Markdown summary."""
import datetime
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

DOMESTIC_FEED_URL = "https://news.google.com/rss/search?q=AI&hl=ja&gl=JP&ceid=JP:ja"
OVERSEAS_FEED_URL = "https://news.google.com/rss/search?q=AI&hl=en-US&gl=US&ceid=US:en"
MAX_ITEMS = 15
MAX_AGE_HOURS = 24
# The unofficial translate.googleapis.com endpoint blocks datacenter IPs
# (including GitHub Actions runners) even though it works from residential
# IPs, so it silently failed on every scheduled run. MyMemory is a public,
# keyless translation API meant for programmatic/CI use.
TRANSLATE_URL = "https://api.mymemory.translated.net/get"


def fetch_feed(url: str) -> ET.Element:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return ET.fromstring(response.read())


def translate_to_ja(text: str) -> str:
    """Translate text to Japanese via the keyless MyMemory API. Falls back to
    the original text (and logs a warning) if translation fails."""
    if not text:
        return text
    params = {"q": text, "langpair": "en|ja"}
    url = TRANSLATE_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        translated = (data.get("responseData") or {}).get("translatedText") or ""
        if not translated or "MYMEMORY WARNING" in translated.upper():
            raise ValueError(f"unusable response: {translated[:120]!r}")
        return translated
    except Exception as exc:
        print(f"warning: translation failed for {text!r}: {exc}", file=sys.stderr)
        return text


def collect_items(root: ET.Element, cutoff: datetime.datetime):
    items = []
    for item in root.findall("./channel/item"):
        pub_date = (item.findtext("pubDate") or "").strip()
        try:
            pub_dt = parsedate_to_datetime(pub_date)
        except (TypeError, ValueError):
            continue
        if pub_dt < cutoff:
            continue
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        source = (item.findtext("source") or "").strip()
        # Google News titles are formatted as "Headline - Source"; strip the
        # trailing source when it duplicates the <source> field.
        if source and title.endswith(f" - {source}"):
            title = title[: -(len(source) + 3)]
        items.append((pub_dt, title, link, source, pub_date))
    items.sort(key=lambda t: t[0], reverse=True)
    return items[:MAX_ITEMS]


def render_section(heading: str, items, translate: bool) -> str:
    if not items:
        return f"### {heading}\n\n直近{MAX_AGE_HOURS}時間以内のニュースは見つかりませんでした。\n"

    lines = [f"### {heading}\n"]
    for _, title, link, source, pub_date in items:
        display_title = title
        if translate:
            display_title = translate_to_ja(title)
            time.sleep(0.3)  # be polite to the unofficial endpoint
        if translate and display_title != title:
            lines.append(
                f"- [{display_title}]({link})  \n  {source} / {pub_date}  \n  原題: {title}"
            )
        else:
            lines.append(f"- [{display_title}]({link})  \n  {source} / {pub_date}")
    return "\n".join(lines)


def main() -> int:
    today = datetime.date.today().isoformat()
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=MAX_AGE_HOURS)

    print(f"## {today} の AI最新ニュース\n")

    try:
        domestic_items = collect_items(fetch_feed(DOMESTIC_FEED_URL), cutoff)
        print(render_section("🇯🇵 国内ニュース", domestic_items, translate=False))
    except Exception as exc:  # network or parse failure shouldn't crash the workflow
        print(f"### 🇯🇵 国内ニュース\n\n取得中にエラーが発生しました: {exc}\n")

    print()

    try:
        overseas_items = collect_items(fetch_feed(OVERSEAS_FEED_URL), cutoff)
        print(render_section("🌍 海外ニュース（日本語訳）", overseas_items, translate=True))
    except Exception as exc:
        print(f"### 🌍 海外ニュース（日本語訳）\n\n取得中にエラーが発生しました: {exc}\n")

    print(
        "\n---\n出典: [Google News検索 \"AI\"]"
        "(https://news.google.com/search?q=AI&hl=ja&gl=JP)"
        "（国内: JP/ja、海外: US/en）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
