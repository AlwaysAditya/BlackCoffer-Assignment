# Blackcoffer: Data Extraction and AI Text Analytics

A Python pipeline that collects article URLs from [insights.blackcoffer.com](https://insights.blackcoffer.com/), extracts each article's title and body text, and computes 13 text-analysis variables per article. Results are saved in the exact column order required by `Output Data Structure.xlsx`.

---

## Table of Contents

1. [Details](#details)
2. [Architecture](#architecture)
3. [Tools & Tech Stack](#tools--tech-stack)
4. [Project Structure](#project-structure)
5. [Setup & Commands](#setup--commands)
6. [Output Variables](#output-variables)
7. [Methodology](#methodology)
8. [Improvements](#improvements)
9. [License](#license)

---

## Details

**Objective:** Extract textual data from articles on `insights.blackcoffer.com` and perform text analysis (sentiment, readability, word statistics).

**What the project does**

| Stage | Description | Output |
|---|---|---|
| 1. URL collection | Fetches 600+ article URLs via the WordPress REST API (falls back to crawling listing pages) | `data/Input.xlsx` |
| 2. Article extraction | Downloads each URL, keeps only the title and article body (no header, footer or sidebar) | `articles/<URL_ID>.txt` |
| 3. Text analysis | Cleans text with stop words, scores sentiment, computes readability and word metrics | in-memory metrics |
| 4. Report generation | Merges input columns with metrics in the template's column order | `Output.xlsx` |

**Key design points**

- Polite scraping: custom `User-Agent`, 1-second delay between requests, 30-second timeouts.
- Fault tolerant: failed URLs are logged to `failed.csv` and do not stop the run.
- Output columns are reindexed from `Output Data Structure.xlsx`, so the order always matches the template.

---

## Architecture

```
                    +--------------------------------+
                    |  insights.blackcoffer.com      |
                    |  (WordPress site)              |
                    +---------------+----------------+
                                    |
              +---------------------+---------------------+
              | 1. /wp-json/wp/v2/posts (API)             |
              |    fallback: /page/N/ HTML crawl          |
              v                                           |
   +-----------------------+                              |
   |  src/collect_urls.py  |                              |
   +-----------+-----------+                              |
               |                                          |
               v                                          |
   +-----------------------+                              |
   |  data/Input.xlsx      |                              |
   |  (URL_ID, URL)        |                              |
   +-----------+-----------+                              |
               |                                          |
               v                                          |
   +-----------------------+   2. HTTP GET each URL       |
   | src/extract_articles  +<-----------------------------+
   |  .py                  |   BeautifulSoup: title + body
   +-----+-----------+-----+
         |           |
         v           v
 +---------------+  +-------------+
 | articles/     |  | failed.csv  |
 | 1.txt, 2.txt  |  | (errors)    |
 +-------+-------+  +-------------+
         |
         v
 +-----------------------+      +--------------------------------+
 |  src/main.py          |----->|  src/analyze.py                |
 |  (orchestrator)       |      |  - tokenize, remove stop words |
 +-----------+-----------+      |  - sentiment dictionaries      |
             ^                  |  - syllables, complex words    |
             |                  |  - readability + pronouns      |
   data/StopWords/              +--------------------------------+
   data/MasterDictionary/
   data/Output Data Structure.xlsx (column order)
             |
             v
   +-----------------------+
   |  Output.xlsx          |
   |  (Input cols + 13     |
   |   text variables)     |
   +-----------------------+
```

**Data flow summary**

```
URLs -> Input.xlsx -> HTML pages -> articles/*.txt -> metrics -> Output.xlsx
```

---

## Tools & Tech Stack

| Category | Tool | Purpose |
|---|---|---|
| Language | Python 3.10+ | Core implementation |
| HTTP | `requests` | Fetching API responses and article pages |
| Parsing | `beautifulsoup4` | Extracting title and body from HTML |
| Data | `pandas` | Reading input, building the output table |
| Excel I/O | `openpyxl` | Reading/writing `.xlsx` files |
| NLP | `nltk` (`punkt`) | Sentence tokenization |
| Text | `re` (stdlib) | Word tokenization, syllables, pronoun matching |
| Environment | `venv` | Isolated dependencies |
| Editor | VS Code | Development |

---

## Project Structure

```
blackcoffer-assignment/
├── data/
│   ├── Input.xlsx                  # URL_ID, URL (generated)
│   ├── Output Data Structure.xlsx  # provided template
│   ├── StopWords/                  # provided stop-word files
│   └── MasterDictionary/           # positive-words.txt, negative-words.txt
├── articles/                       # extracted text files (1.txt, 2.txt, ...)
├── src/
│   ├── collect_urls.py             # builds Input.xlsx
│   ├── extract_articles.py         # Input.xlsx -> articles/*.txt
│   ├── analyze.py                  # text-analysis functions
│   └── main.py                     # runs analysis -> Output.xlsx
├── failed.csv                      # URLs that failed extraction
├── Output.xlsx                     # final result
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Setup & Commands

### Prerequisites

- Python 3.10 or newer
- The assignment's provided files: `Output Data Structure.xlsx`, stop-word files, and the positive/negative dictionaries

### 1. Create the environment

**Windows (PowerShell)**
```powershell
py -m venv venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # once, if scripts are blocked
.\venv\Scripts\Activate.ps1
```

**Mac/Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

`requirements.txt`
```
requests
beautifulsoup4
pandas
openpyxl
nltk
```

### 3. Add the provided files

| File | Location |
|---|---|
| `Output Data Structure.xlsx` | `data/` |
| Stop-word `.txt` files | `data/StopWords/` |
| `positive-words.txt`, `negative-words.txt` | `data/MasterDictionary/` |

### 4. Run the pipeline

```bash
python src/collect_urls.py       # creates data/Input.xlsx (~10-30 sec)
python src/extract_articles.py   # creates articles/*.txt (~15-20 min)
python src/main.py               # creates Output.xlsx (few seconds)
```

### 5. Verify

```bash
# Input has 600+ rows
python -c "import pandas as pd; df = pd.read_excel('data/Input.xlsx'); print(df.columns.tolist(), len(df))"

# Output metrics are filled
python -c "import pandas as pd; df = pd.read_excel('Output.xlsx'); print(df.head()); print(df.isna().sum())"
```

**PowerShell checks**
```powershell
(Get-ChildItem articles).Count     # number of saved articles
notepad articles\1.txt             # spot-check: title + body only
```

---

## Output Variables

`Output.xlsx` contains the input columns followed by:

| # | Variable |
|---|---|
| 1 | POSITIVE SCORE |
| 2 | NEGATIVE SCORE |
| 3 | POLARITY SCORE |
| 4 | SUBJECTIVITY SCORE |
| 5 | AVG SENTENCE LENGTH |
| 6 | PERCENTAGE OF COMPLEX WORDS |
| 7 | FOG INDEX |
| 8 | AVG NUMBER OF WORDS PER SENTENCE |
| 9 | COMPLEX WORD COUNT |
| 10 | WORD COUNT |
| 11 | SYLLABLE PER WORD |
| 12 | PERSONAL PRONOUNS |
| 13 | AVG WORD LENGTH |

---

## Methodology

**Text cleaning:** sentences are split with NLTK; words are extracted with a letters-only regex, lowercased, and filtered against the stop-word list.

| Variable | Formula |
|---|---|
| Positive / Negative score | Count of cleaned words found in the positive / negative dictionary (stop words removed from both) |
| Polarity score | `(Pos - Neg) / ((Pos + Neg) + 0.000001)` |
| Subjectivity score | `(Pos + Neg) / (Total cleaned words + 0.000001)` |
| Avg sentence length | `Total cleaned words / Total sentences` |
| Complex word count | Words with more than 2 syllables |
| Percentage of complex words | `Complex words / Total cleaned words` |
| Fog index | `0.4 * (Avg sentence length + Percentage of complex words)` |
| Avg words per sentence | `Total cleaned words / Total sentences` |
| Word count | Total cleaned words (stop words and punctuation removed) |
| Syllables per word | Vowel-group count per word; trailing `es` / `ed` not counted |
| Personal pronouns | Regex matches for `I, we, my, ours, us`; the country name "US" is excluded |
| Avg word length | `Total characters in cleaned words / Total cleaned words` |

---

## Improvements

**Scraping**
- Add concurrent downloads (`concurrent.futures` or `aiohttp`) to cut extraction from ~15 minutes to a few.
- Add automatic retries with exponential backoff for failed URLs.
- Cache downloaded HTML so selector changes don't require re-downloading.
- Use `Selenium` or `Playwright` as a fallback for JavaScript-rendered pages.

**Analysis**
- Use a pronunciation dictionary (e.g. `pyphen` or `cmudict`) for more accurate syllable counts.
- Improve pronoun detection with a POS tagger.
- Add negation handling (e.g. "not good") to sentiment scoring.
- Cache stop-word and dictionary loading across runs.

**Engineering**
- Add a single CLI entry point (`python run.py --all`) with `argparse`.
- Replace `print` with structured logging.
- Add unit tests (`pytest`) for the metric functions.
- Move CSS selectors and settings to a config file.
- Add a GitHub Actions workflow for linting and tests.

**Output**
- Add a summary notebook with charts of sentiment and readability distributions.
- Add a validation step that flags empty or very short articles.

---

## Author

**Aditya Salani**
[GitHub](https://github.com/AlwaysAditya) | [LinkedIn](https://linkedin.com/in/adityasalani) | [Portfolio](https://adityasalaniportfolio.vercel.app)

---

## License

This project is licensed under the [MIT License](LICENSE).

---
