import json
import re
import pickle
import sys
from collections import defaultdict

DOCS_PATH = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\wiki_docs.jsonl"
GRAPH_OUT = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\graph_10k.pkl"

LIMIT_DOCS = 10_000  # مطابق ایندکس‌سازی تو

# لینک‌های ویکی در متن معمولاً این شکلی‌اند: [[Title]] یا [[Title|anchor]]
WIKI_LINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")

def normalize_title(t: str) -> str:
    t = t.strip()
    if not t:
        return t
    # حذف anchor بعد از |
    if "|" in t:
        t = t.split("|", 1)[0]
    # حذف بخش بعد از # (section)
    if "#" in t:
        t = t.split("#", 1)[0]
    t = t.strip().replace("_", " ")
    # Title-case کامل نمی‌کنیم؛ فقط یکسان‌سازی ساده:
    # ویکی‌پدیا حرف اول بزرگ است، ولی برای نگاشت ما یک روش پایدار انتخاب می‌کنیم:
    return t

def extract_links(text: str):
    for m in WIKI_LINK_RE.finditer(text):
        yield normalize_title(m.group(1))

def build_title_to_id(path: str, limit_docs: int):
    title2id = {}
    docs = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            obj = json.loads(line)
            doc_id = int(obj["id"])
            title = obj["title"]
            title2id[normalize_title(title)] = doc_id
            docs.append(obj)
            if i >= limit_docs:
                break
    return title2id, docs

def build_graph(docs, title2id):
    g = defaultdict(set)
    for obj in docs:
        src = int(obj["id"])
        text = obj.get("text", "")
        for t in extract_links(text):
            dst = title2id.get(t)
            if dst is not None and dst != src:
                g[src].add(dst)
        # مطمئن شو هر نود کلید داشته باشه حتی اگر خروجی نداشت
        g[src]
    # set -> list
    return {u: list(vs) for u, vs in g.items()}

if __name__ == "__main__":
    print("Building title->id for first docs...", file=sys.stderr)
    title2id, docs = build_title_to_id(DOCS_PATH, LIMIT_DOCS)
    print("docs loaded:", len(docs), "titles:", len(title2id), file=sys.stderr)

    print("Extracting links & building graph...", file=sys.stderr)
    graph = build_graph(docs, title2id)

    # آمار ساده
    V = len(graph)
    E = sum(len(graph[u]) for u in graph)

    with open(GRAPH_OUT, "wb") as f:
        pickle.dump({"graph": graph, "V": V, "E": E}, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Saved graph to: {GRAPH_OUT}", file=sys.stderr)
    print("V =", V)
    print("E =", E)
