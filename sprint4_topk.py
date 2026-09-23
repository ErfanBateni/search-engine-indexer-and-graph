import json
import heapq

DOCS_PATH = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\wiki_docs.jsonl"
K = 10

def iter_docs(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            yield obj["id"], len(obj["text"])

def top_k_longest_docs(k: int):
    heap = []  # min-heap

    for doc_id, length in iter_docs(DOCS_PATH):
        if len(heap) < k:
            heapq.heappush(heap, (length, doc_id))
        else:
            if length > heap[0][0]:
                heapq.heapreplace(heap, (length, doc_id))

    return sorted(heap, reverse=True)

if __name__ == "__main__":
    res = top_k_longest_docs(K)
    print(f"Top-{K} longest documents:")
    for length, doc_id in res:
        print(f"doc_id={doc_id}, length={length}")