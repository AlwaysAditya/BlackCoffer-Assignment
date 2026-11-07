import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

BASE = "https://insights.blackcoffer.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUT = Path(__file__).parent.parent / "data" / "Input.xlsx"
TARGET = 650


def via_api():
    urls, page = [], 1
    while len(urls) < TARGET:
        r = requests.get(f"{BASE}/wp-json/wp/v2/posts",
                         params={"per_page": 100, "page": page, "_fields": "link"},
                         headers=HEADERS, timeout=30)
        if r.status_code != 200:
            break
        data = r.json()
        if not data:
            break
        urls += [p["link"] for p in data]
        page += 1
        time.sleep(1)
    return urls


def via_crawl():
    urls, page = [], 1
    while len(urls) < TARGET:
        r = requests.get(f"{BASE}/page/{page}/", headers=HEADERS, timeout=30)
        if r.status_code != 200:
            break
        soup = BeautifulSoup(r.text, "html.parser")
        links = [a["href"] for h in soup.select("h3.entry-title a, h2.entry-title a") for a in [h]]
        if not links:
            break
        urls += links
        page += 1
        time.sleep(1)
    return urls


urls = via_api() or via_crawl()
urls = list(dict.fromkeys(urls))  # dedupe, keep order
df = pd.DataFrame({"URL_ID": range(1, len(urls) + 1), "URL": urls})
df.to_excel(OUT, index=False)
print(f"Saved {len(df)} URLs -> {OUT}")