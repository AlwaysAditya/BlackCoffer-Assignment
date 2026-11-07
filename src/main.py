import pandas as pd
from pathlib import Path
from analyze import analyze

ROOT = Path(__file__).parent.parent
df = pd.read_excel(ROOT / "data" / "Input.xlsx")
template_cols = list(pd.read_excel(ROOT / "data" / "Output Data Structure.xlsx").columns)

rows = []
for _, r in df.iterrows():
    f = ROOT / "articles" / f"{r['URL_ID']}.txt"
    metrics = analyze(f.read_text(encoding="utf-8")) if f.exists() else {}
    rows.append({"URL_ID": r["URL_ID"], "URL": r["URL"], **metrics})

out = pd.DataFrame(rows).reindex(columns=template_cols)  # exact template order
out.to_excel(ROOT / "Output.xlsx", index=False)
print(f"Saved {len(out)} rows -> Output.xlsx")