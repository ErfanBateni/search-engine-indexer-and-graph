import json
import math
import time
import tracemalloc
from typing import Iterable, Tuple


INPUT_PATH = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\page_meta.jsonl"
# برای شروع، همون 1 میلیون که داری هم می‌تونه باشه، ولی من پیشنهاد می‌کنم اول 200k تست کنی
LIMIT = 10_000


def iter_titles(path: str, limit: int | None = None) -> Iterable[str]:
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            title = obj.get("title", "")
            if title:
                yield title
                n += 1
                if limit is not None and n >= limit:
                    return


# -------------------------
# Hash 64-bit (FNV-1a)
# -------------------------
def fnv1a_64(s: str) -> int:
    h = 1469598103934665603  # offset basis
    fnv_prime = 1099511628211
    data = s.encode("utf-8", errors="ignore")
    for b in data:
        h ^= b
        h = (h * fnv_prime) & 0xFFFFFFFFFFFFFFFF
    return h


# -------------------------
# Bloom Filter
# -------------------------
class BloomFilter:
    def __init__(self, m_bits: int, k_hashes: int):
        self.m = m_bits
        self.k = k_hashes
        self.bytes = bytearray((m_bits + 7) // 8)

    def _set_bit(self, idx: int):
        byte_i = idx >> 3
        bit_i = idx & 7
        self.bytes[byte_i] |= (1 << bit_i)

    def _get_bit(self, idx: int) -> int:
        byte_i = idx >> 3
        bit_i = idx & 7
        return (self.bytes[byte_i] >> bit_i) & 1

    def add(self, h1: int, h2: int):
        # double hashing: h_i = h1 + i*h2
        for i in range(self.k):
            idx = (h1 + i * h2) % self.m
            self._set_bit(idx)

    def contains(self, h1: int, h2: int) -> bool:
        for i in range(self.k):
            idx = (h1 + i * h2) % self.m
            if self._get_bit(idx) == 0:
                return False
        return True


def bloom_params(n: int, fp_rate: float) -> Tuple[int, int]:
    # m = -n ln(p) / (ln2^2)
    # k = (m/n) ln2
    ln2 = math.log(2)
    m = int(-n * math.log(fp_rate) / (ln2 ** 2))
    k = max(1, int((m / n) * ln2))
    return m, k


# -------------------------
# Benchmark helpers
# -------------------------
def measure(fn, *args, **kwargs):
    tracemalloc.start()
    t0 = time.time()
    result = fn(*args, **kwargs)
    dt = time.time() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, dt, peak


# -------------------------
# Method 1: set of strings
# -------------------------
def dedup_set_strings(titles: Iterable[str]) -> int:
    s = set()
    for t in titles:
        s.add(t)
    return len(s)


# -------------------------
# Method 2: set of 64-bit hashes
# -------------------------
def dedup_set_hash64(titles: Iterable[str]) -> int:
    s = set()
    for t in titles:
        s.add(fnv1a_64(t))
    return len(s)


# -------------------------
# Method 3: bloom filter (approx unique count)
# NOTE: bloom خودش "تعداد یکتا" را دقیق نمی‌دهد.
# ما فقط نرخ "قبلاً دیده شده" را با bloom می‌سنجیم.
# -------------------------
def dedup_bloom_seen_ratio(titles: Iterable[str], expected_n: int, fp_rate: float = 0.01):
    m, k = bloom_params(expected_n, fp_rate)
    bf = BloomFilter(m, k)

    seen = 0
    total = 0

    for t in titles:
        total += 1
        h1 = fnv1a_64(t)
        h2 = fnv1a_64("salt|" + t) | 1  # h2 فرد باشد بهتر پخش می‌شود

        if bf.contains(h1, h2):
            seen += 1
        else:
            bf.add(h1, h2)

    # seen_ratio هرچقدر کمتر باشد یعنی "تکراری کمتر"؛ bloom احتمالاً کمی اغراق می‌کند (false positive)
    return {"total": total, "seen_as_duplicate": seen, "seen_ratio": seen / total if total else 0, "m_bits": m, "k": k}


if __name__ == "__main__":
    print("INPUT:", INPUT_PATH)
    print("LIMIT:", LIMIT)

    titles1 = iter_titles(INPUT_PATH, LIMIT)
    titles2 = iter_titles(INPUT_PATH, LIMIT)
    titles3 = iter_titles(INPUT_PATH, LIMIT)

    # روش 1
    uniq1, dt1, peak1 = measure(dedup_set_strings, titles1)

    # روش 2
    uniq2, dt2, peak2 = measure(dedup_set_hash64, titles2)

    # روش 3 (Bloom)
    bloom_res, dt3, peak3 = measure(dedup_bloom_seen_ratio, titles3, expected_n=LIMIT, fp_rate=0.01)

    print("\n=== RESULTS ===")
    print(f"1) Set<String> unique={uniq1} time={dt1:.2f}s peak_mem={peak1/1024/1024:.2f} MB")
    print(f"2) Set<Hash64> unique={uniq2} time={dt2:.2f}s peak_mem={peak2/1024/1024:.2f} MB")
    print(f"3) BloomFilter   seen_ratio={bloom_res['seen_ratio']:.4f} "
          f"time={dt3:.2f}s peak_mem={peak3/1024/1024:.2f} MB "
          f"(m_bits={bloom_res['m_bits']}, k={bloom_res['k']})")