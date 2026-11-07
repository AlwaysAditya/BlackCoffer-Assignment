import re
from pathlib import Path
from nltk.tokenize import sent_tokenize

DATA = Path(__file__).parent.parent / "data"


def _read_words(folder, pattern="*.txt"):
    words = set()
    for f in Path(folder).glob(pattern):
        for line in f.read_text(encoding="latin-1").splitlines():
            w = line.split("|")[0].strip().lower()
            if w:
                words.add(w)
    return words


STOP = _read_words(DATA / "StopWords")
POS = _read_words(DATA / "MasterDictionary", "positive-words.txt") - STOP
NEG = _read_words(DATA / "MasterDictionary", "negative-words.txt") - STOP


def syllables(word):
    word = word.lower()
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith(("es", "ed")) and count > 1:
        count -= 1
    return max(count, 1)


def analyze(text):
    sentences = sent_tokenize(text)
    tokens = re.findall(r"[A-Za-z]+", text)
    words = [w.lower() for w in tokens if w.lower() not in STOP]

    n_words = len(words)
    n_sent = max(len(sentences), 1)

    pos = sum(w in POS for w in words)
    neg = sum(w in NEG for w in words)
    polarity = (pos - neg) / ((pos + neg) + 0.000001)
    subjectivity = (pos + neg) / (n_words + 0.000001)

    syl = [syllables(w) for w in words]
    complex_count = sum(s > 2 for s in syl)

    avg_sent_len = n_words / n_sent
    pct_complex = complex_count / n_words if n_words else 0
    fog = 0.4 * (avg_sent_len + pct_complex)

    pronouns = [m for m in re.findall(r"\b(?:I|we|my|ours|us)\b", text, re.I) if m != "US"]

    return {
        "POSITIVE SCORE": pos,
        "NEGATIVE SCORE": neg,
        "POLARITY SCORE": polarity,
        "SUBJECTIVITY SCORE": subjectivity,
        "AVG SENTENCE LENGTH": avg_sent_len,
        "PERCENTAGE OF COMPLEX WORDS": pct_complex,
        "FOG INDEX": fog,
        "AVG NUMBER OF WORDS PER SENTENCE": avg_sent_len,
        "COMPLEX WORD COUNT": complex_count,
        "WORD COUNT": n_words,
        "SYLLABLE PER WORD": sum(syl) / n_words if n_words else 0,
        "PERSONAL PRONOUNS": len(pronouns),
        "AVG WORD LENGTH": sum(len(w) for w in words) / n_words if n_words else 0,
    }