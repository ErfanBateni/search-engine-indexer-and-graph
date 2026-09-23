import json
import bisect
import random
import time
from dataclasses import dataclass

DOCS_PATH = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\wiki_docs.jsonl"

# تعداد اسناد برای ساخت داده (اگر خیلی سنگین شد کمش کن)
LIMIT_DOCS = None  # یا مثلا 50000

# تعداد کوئری‌های تصادفی برای بنچمارک
Q = 2000

# بازه‌های تست: (low, high)
# هم بازه کوچک، هم متوسط، هم بزرگ
QUERY_RANGES = [
    (200, 300),
    (500, 1000),
    (2000, 5000),
]

# -----------------------------
# Data loader: (length, doc_id)
# -----------------------------
def load_lengths(path: str, limit_docs=None):
    arr = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            obj = json.loads(line)
            arr.append((len(obj["text"]), int(obj["id"])))
            if limit_docs is not None and i >= limit_docs:
                break
    return arr

# -----------------------------
# Method 1: Linear Scan
# -----------------------------
def range_scan(arr, low, high):
    out = []
    for length, doc_id in arr:
        if low <= length <= high:
            out.append((length, doc_id))
    return out

# -----------------------------
# Method 2: Sorted Array + Bisect
# -----------------------------
def build_sorted(arr):
    a = arr[:]  # copy
    a.sort()
    return a

def range_bisect(sorted_arr, low, high):
    left = bisect.bisect_left(sorted_arr, (low, -1))
    right = bisect.bisect_right(sorted_arr, (high, 10**18))
    return sorted_arr[left:right]

# -----------------------------
# Method 3: Treap (Balanced BST)
# -----------------------------
@dataclass
class Node:
    key: tuple  # (length, doc_id)
    pr: int
    left: "Node | None" = None
    right: "Node | None" = None

def rotate_right(p: Node) -> Node:
    q = p.left
    p.left = q.right
    q.right = p
    return q

def rotate_left(p: Node) -> Node:
    q = p.right
    p.right = q.left
    q.left = p
    return q

def treap_insert(root: Node | None, key: tuple) -> Node:
    if root is None:
        return Node(key=key, pr=random.randint(1, 10**9))

    if key < root.key:
        root.left = treap_insert(root.left, key)
        if root.left.pr < root.pr:
            root = rotate_right(root)
    else:
        root.right = treap_insert(root.right, key)
        if root.right.pr < root.pr:
            root = rotate_left(root)
    return root

def treap_range_query(root: Node | None, low: int, high: int, out: list):
    if root is None:
        return
    length = root.key[0]

    # اگر length بزرگتر از low است، سمت چپ ممکن است جواب داشته باشد
    if length >= low:
        treap_range_query(root.left, low, high, out)

    if low <= length <= high:
        out.append(root.key)

    # اگر length کوچکتر از high است، سمت راست ممکن است جواب داشته باشد
    if length <= high:
        treap_range_query(root.right, low, high, out)

def build_treap(arr):
    root = None
    for key in arr:
        root = treap_insert(root, key)
    return root

def range_treap(root, low, high):
    out = []
    treap_range_query(root, low, high, out)
    return out

# -----------------------------
# Benchmark helper
# -----------------------------
def bench(method_name, build_fn, query_fn, arr, ranges, repeats):
    # build
    t0 = time.perf_counter()
    structure = build_fn(arr)
    build_ms = (time.perf_counter() - t0) * 1000

    # query
    total_hits = 0
    t0 = time.perf_counter()
    for _ in range(repeats):
        for low, high in ranges:
            res = query_fn(structure, low, high)
            total_hits += len(res)
    query_ms = (time.perf_counter() - t0) * 1000

    return {
        "method": method_name,
        "build_ms": build_ms,
        "query_ms": query_ms,
        "avg_query_ms": query_ms / (repeats * len(ranges)),
        "total_hits": total_hits
    }

# wrappers for uniform signature
def build_identity(arr): return arr
def query_scan(struct, low, high): return range_scan(struct, low, high)

def query_bisect(struct, low, high): return range_bisect(struct, low, high)

def query_treap(struct, low, high): return range_treap(struct, low, high)

if __name__ == "__main__":
    random.seed(42)

    print("Loading docs lengths...")
    arr = load_lengths(DOCS_PATH, LIMIT_DOCS)
    print("docs:", len(arr))

    # روش 1: scan
    r1 = bench("Linear Scan", build_identity, query_scan, arr, QUERY_RANGES, Q)

    # روش 2: sorted+bisect
    r2 = bench("Sorted Array + Bisect", build_sorted, query_bisect, arr, QUERY_RANGES, Q)

    # روش 3: Treap (BST متوازن)
    r3 = bench("Treap (Balanced BST)", build_treap, query_treap, arr, QUERY_RANGES, Q)

    print("\n=== RANGE QUERY BENCHMARK ===")
    for r in [r1, r2, r3]:
        print(f"{r['method']}")
        print(f"  build_ms     : {r['build_ms']:.2f}")
        print(f"  query_ms     : {r['query_ms']:.2f}")
        print(f"  avg_query_ms : {r['avg_query_ms']:.6f}")
        print(f"  total_hits   : {r['total_hits']}")