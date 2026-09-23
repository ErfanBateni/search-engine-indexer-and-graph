import pickle
import re
import time

LEXICON_PATH = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\compressed_lexicon.pkl"
POSTINGS_PATH = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\compressed_postings.bin"

TOKEN_RE = re.compile(r"[a-z0-9]+")

def norm_term(q: str) -> str:
    m = TOKEN_RE.findall(q.lower())
    return m[0] if m else ""

# -------- VB decode ----------
def vb_decode_stream(b: bytes):
    n = 0
    for byte in b:
        if byte & 0x80:  # last byte
            n = (n << 7) | (byte & 0x7F)
            yield n
            n = 0
        else:
            n = (n << 7) | byte

def delta_decode(gaps):
    out = []
    cur = 0
    for g in gaps:
        cur += g
        out.append(cur)
    return out

if __name__ == "__main__":
    with open(LEXICON_PATH, "rb") as f:
        meta = pickle.load(f)
    lexicon = meta["lexicon"]
    stats = meta["stats"]
    print("Loaded compressed index stats:", stats)

    with open(POSTINGS_PATH, "rb") as f:
        postings_blob = f.read()

    while True:
        q = input("\nEnter a single word (or 'exit'): ").strip()
        if q.lower() == "exit":
            break
        term = norm_term(q)
        if not term:
            print("Bad query.")
            continue

        info = lexicon.get(term)
        if not info:
            print(f"term='{term}' -> results=0")
            continue

        offset, length, df = info

        t0 = time.perf_counter()
        chunk = postings_blob[offset: offset + length]
        gaps = list(vb_decode_stream(chunk))
        postings = delta_decode(gaps)
        dt_ms = (time.perf_counter() - t0) * 1000

        print(f"term='{term}' -> results={len(postings)} df={df} (decompress_time={dt_ms:.3f} ms)")
        print("first 20 doc_ids:", postings[:20])