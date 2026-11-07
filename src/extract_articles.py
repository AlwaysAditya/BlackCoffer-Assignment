import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

ROOT = Path(__file__).parent.parent
HEADERS = {"User-Agent": "Mozilla/5.0"}
TITLE_SEL = ["h1.entry-title", "h1.tdb-title-text", "h1"]
BODY_SEL = ["div.td-post-content", "div.tdb-block-inner", "div.entry-content", "article"]


def first(soup, selectors):
    for s in selectors:
        el = soup.select_one(s)
        if el:
            return el
    return None


df = pd.read_excel(ROOT / "data" / "Input.xlsx")
failed = []

for _, row in df.iterrows():
    uid, url = row["URL_ID"], row["URL"]
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title, body = first(soup, TITLE_SEL), first(soup, BODY_SEL)
        if not (title and body):
            raise ValueError("selectors not found")
        for junk in body.select("script, style, nav, footer, .td-post-sharing, .comments"):
            junk.decompose()
        text = title.get_text(strip=True) + "\n\n" + body.get_text("\n", strip=True)
        (ROOT / "articles" / f"{uid}.txt").write_text(text, encoding="utf-8")
        print(f"OK   {uid}")
    except Exception as e:
        failed.append((uid, url, str(e)))
        print(f"FAIL {uid}: {e}")
    time.sleep(1)

pd.DataFrame(failed, columns=["URL_ID", "URL", "error"]).to_csv(ROOT / "failed.csv", index=False)