import pickle
import time

RAW_INDEX = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\inverted_index.pkl"
LEXICON_PATH = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\compressed_lexicon.pkl"
POSTINGS_PATH = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\compressed_postings.bin"

TERMS = ["the", "history", "computer"]
REPEATS = 2000

def vb_decode_stream(b: bytes):
    n = 0
    for byte in b:
        if byte & 0x80:
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
    with open(RAW_INDEX, "rb") as f:
        raw = pickle.load(f)["index"]

    with open(LEXICON_PATH, "rb") as f:
        lex = pickle.load(f)["lexicon"]

    with open(POSTINGS_PATH, "rb") as f:
        blob = f.read()

    print("=== BENCHMARK ===")
    print("TERMS:", TERMS, "REPEATS:", REPEATS)

    # 1) بدون فشرده‌سازی (فقط dict lookup)
    t0 = time.perf_counter()
    total = 0
    for _ in range(REPEATS):
        for term in TERMS:
            total += len(raw.get(term, []))
    dt1 = (time.perf_counter() - t0) * 1000
    print(f"RAW lookup total_time={dt1:.2f} ms (dummy_total={total})")

    # 2) با فشرده‌سازی (lookup + decompress)
    t0 = time.perf_counter()
    total = 0
    for _ in range(REPEATS):
        for term in TERMS:
            info = lex.get(term)
            if not info:
                continue
            off, ln, df = info
            chunk = blob[off:off+ln]
            gaps = vb_decode_stream(chunk)
            postings = delta_decode(gaps)
            total += len(postings)
    dt2 = (time.perf_counter() - t0) * 1000
    print(f"COMPRESSED lookup+decompress total_time={dt2:.2f} ms (dummy_total={total})")

    print("avg_per_query_raw_ms:", round(dt1 / (REPEATS * len(TERMS)), 6))
    print("avg_per_query_compressed_ms:", round(dt2 / (REPEATS * len(TERMS)), 6))