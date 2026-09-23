import json
import pickle
import re
import sys
import time
from collections import defaultdict

DOCS_PATH = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\wiki_docs.jsonl"
INDEX_OUT = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\inverted_index.pkl"

# برای شروع. اگر کند/سنگین بود کمش کن. اگر سریع بود زیادش کن.
LIMIT_DOCS = 10_000

# توکنایزر ساده و قابل دفاع
TOKEN_RE = re.compile(r"[a-z0-9]+")

def tokenize(text: str):
    # lowercase + فقط a-z0-9
    for tok in TOKEN_RE.findall(text.lower()):
        if len(tok) >= 2:
            yield tok

def build_inverted_index(path: str, limit_docs: int | None = None):
    index = defaultdict(list)
    n_docs = 0
    n_tokens_total = 0

    t0 = time.time()
    with open(path, encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            doc_id = int(obj["id"])
            text = obj.get("text", "")

            # برای اینکه یک کلمه در یک سند چندبار تکرار شده، doc_id دوباره ثبت نشه:
            seen_terms = set()
            for tok in tokenize(text):
                n_tokens_total += 1
                seen_terms.add(tok)

            for term in seen_terms:
                index[term].append(doc_id)

            n_docs += 1
            if n_docs % 1000 == 0:
                print(f"processed docs: {n_docs}", file=sys.stderr)

            if limit_docs is not None and n_docs >= limit_docs:
                break

    # مرتب‌سازی postings list ها (مهم برای delta)
    for term in index:
        index[term].sort()

    dt = time.time() - t0
    stats = {
        "docs_indexed": n_docs,
        "unique_terms": len(index),
        "tokens_scanned": n_tokens_total,
        "build_time_sec": round(dt, 2),
    }
    return dict(index), stats

if __name__ == "__main__":
    idx, stats = build_inverted_index(DOCS_PATH, LIMIT_DOCS)

    with open(INDEX_OUT, "wb") as f:
        pickle.dump({"index": idx, "stats": stats}, f, protocol=pickle.HIGHEST_PROTOCOL)

    print("\n=== BUILD STATS ===")
    for k, v in stats.items():
        print(f"{k}: {v}")
    print(f"saved: {INDEX_OUT}")