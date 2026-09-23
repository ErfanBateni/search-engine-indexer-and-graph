import json
import bisect

DOCS_PATH = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\wiki_docs.jsonl"

def build_sorted_by_length():
    arr = []
    with open(DOCS_PATH, encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            arr.append((len(obj["text"]), obj["id"]))
    arr.sort()
    return arr

def range_query(arr, low, high):
    left = bisect.bisect_left(arr, (low, -1))
    right = bisect.bisect_right(arr, (high, float("inf")))
    return arr[left:right]

if __name__ == "__main__":
    arr = build_sorted_by_length()
    res = range_query(arr, 500, 1000)
    print(f"Documents with length in [500,1000]: {len(res)}")
    print("First 10:", res[:10])