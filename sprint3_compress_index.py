import os
import pickle
import sys
import time

INDEX_IN = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\inverted_index.pkl"
LEXICON_OUT = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\compressed_lexicon.pkl"
POSTINGS_OUT = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\compressed_postings.bin"

# -------- Variable-Byte Encoding / Decoding --------
def vb_encode_number(n: int) -> bytes:
    # encode non-negative integer
    if n < 0:
        raise ValueError("vb_encode_number expects non-negative integer")
    bytes_list = []
    while True:
        bytes_list.append(n & 0x7F)  # 7 bits
        n >>= 7
        if n == 0:
            break
    # mark last byte with continuation bit = 1
    bytes_list[0] |= 0x80
    return bytes(bytearray(reversed(bytes_list)))

def vb_encode_list(nums):
    out = bytearray()
    for n in nums:
        out.extend(vb_encode_number(n))
    return bytes(out)

def delta_encode(sorted_ids):
    # [d1, d2, d3] -> [d1, d2-d1, d3-d2]
    if not sorted_ids:
        return []
    gaps = [sorted_ids[0]]
    for i in range(1, len(sorted_ids)):
        gaps.append(sorted_ids[i] - sorted_ids[i-1])
    return gaps

# -----------------------------------------------
def compress_index(index: dict):
    """
    خروجی:
      lexicon: term -> (offset, length, df)
      postings_bytes: bytes concatenated
    """
    lexicon = {}
    postings_blob = bytearray()

    # برای سرعت/یکنواختی: ترم‌ها را مرتب می‌کنیم
    terms = sorted(index.keys())

    for i, term in enumerate(terms, 1):
        postings = index[term]  # sorted list of doc_ids
        gaps = delta_encode(postings)
        enc = vb_encode_list(gaps)

        offset = len(postings_blob)
        postings_blob.extend(enc)
        length = len(enc)
        df = len(postings)

        lexicon[term] = (offset, length, df)

        if i % 200000 == 0:
            print(f"compressed terms: {i}/{len(terms)}", file=sys.stderr)

    return lexicon, bytes(postings_blob)

if __name__ == "__main__":
    t0 = time.time()
    with open(INDEX_IN, "rb") as f:
        data = pickle.load(f)

    index = data["index"]
    stats = data["stats"]
    print("Loaded index stats:", stats)

    lexicon, postings_blob = compress_index(index)

    # ذخیره postings به صورت باینری
    with open(POSTINGS_OUT, "wb") as f:
        f.write(postings_blob)

    # ذخیره lexicon
    with open(LEXICON_OUT, "wb") as f:
        pickle.dump({"lexicon": lexicon, "stats": stats}, f, protocol=pickle.HIGHEST_PROTOCOL)

    dt = time.time() - t0

    raw_size = os.path.getsize(INDEX_IN)
    lex_size = os.path.getsize(LEXICON_OUT)
    post_size = os.path.getsize(POSTINGS_OUT)

    print("\n=== COMPRESSION STATS ===")
    print("time_sec:", round(dt, 2))
    print("terms:", len(lexicon))
    print("raw_index_pkl_size_MB:", round(raw_size / 1024 / 1024, 2))
    print("lexicon_pkl_size_MB:", round(lex_size / 1024 / 1024, 2))
    print("postings_bin_size_MB:", round(post_size / 1024 / 1024, 2))
    print("total_compressed_MB:", round((lex_size + post_size) / 1024 / 1024, 2))
    print("saved:", LEXICON_OUT)
    print("saved:", POSTINGS_OUT)