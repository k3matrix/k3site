#!/usr/bin/env python3
"""Submit all sitemap URLs to IndexNow so search engines re-crawl on push."""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "k3matrix.com.tr"
KEY = "4b6363b04ba630e9243c437b0ddc8492"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"

REPO_ROOT = Path(__file__).resolve().parent.parent
SITEMAP_PATH = REPO_ROOT / "sitemap.xml"


def load_urls_from_sitemap(path: Path) -> list[str]:
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(path)
    return [loc.text.strip() for loc in tree.getroot().findall("sm:url/sm:loc", ns) if loc.text]


def submit(urls: list[str]) -> None:
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"IndexNow response: {resp.status} {resp.reason}")
    except urllib.error.HTTPError as e:
        print(f"IndexNow response: {e.code} {e.reason}")
        print(e.read().decode("utf-8", errors="replace"))
        sys.exit(1)


def main() -> None:
    urls = load_urls_from_sitemap(SITEMAP_PATH)
    if not urls:
        print("No URLs found in sitemap.xml", file=sys.stderr)
        sys.exit(1)
    print(f"Submitting {len(urls)} URLs to IndexNow:")
    for u in urls:
        print(f"  {u}")
    submit(urls)


if __name__ == "__main__":
    main()
