import pickle
import re
import time

INDEX_PATH = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\inverted_index.pkl"

TOKEN_RE = re.compile(r"[a-z0-9]+")

def norm_term(q: str) -> str:
    m = TOKEN_RE.findall(q.lower())
    return m[0] if m else ""

if __name__ == "__main__":
    with open(INDEX_PATH, "rb") as f:
        data = pickle.load(f)

    index = data["index"]
    stats = data["stats"]
    print("Loaded index. Stats:", stats)

    while True:
        q = input("\nEnter a single word (or 'exit'): ").strip()
        if q.lower() == "exit":
            break
        term = norm_term(q)
        if not term:
            print("Bad query.")
            continue

        t0 = time.time()
        postings = index.get(term, [])
        dt = (time.time() - t0) * 1000

        print(f"term='{term}' -> results={len(postings)}  (lookup_time={dt:.3f} ms)")
        print("first 20 doc_ids:", postings[:20])