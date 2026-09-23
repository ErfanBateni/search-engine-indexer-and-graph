import pickle
import time
from collections import defaultdict


GRAPH_IN = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\graph_10k.pkl"


# ---------------------------
# 1) Tarjan SCC (Iterative)
# ---------------------------
def tarjan_scc_iterative(graph: dict[int, list[int]]):
    index = 0
    indices = {}
    low = {}
    S = []
    onS = set()
    sccs = []

    # call stack frames: (v, next_neighbor_index, parent)
    for start in graph.keys():
        if start in indices:
            continue

        stack = [(start, 0, None)]
        while stack:
            v, ni, parent = stack[-1]

            # first time we see v
            if v not in indices:
                indices[v] = index
                low[v] = index
                index += 1
                S.append(v)
                onS.add(v)

            neigh = graph.get(v, [])
            if ni < len(neigh):
                w = neigh[ni]
                # advance neighbor index
                stack[-1] = (v, ni + 1, parent)

                if w not in indices:
                    stack.append((w, 0, v))
                elif w in onS:
                    low[v] = min(low[v], indices[w])
            else:
                # finished v
                stack.pop()

                # update parent's lowlink after child finished
                if parent is not None:
                    low[parent] = min(low[parent], low[v])

                # root of SCC?
                if low[v] == indices[v]:
                    comp = []
                    while True:
                        w = S.pop()
                        onS.remove(w)
                        comp.append(w)
                        if w == v:
                            break
                    sccs.append(comp)

    return sccs


# ---------------------------
# 2) Kosaraju SCC (Iterative)
# ---------------------------
def build_reverse_graph(graph: dict[int, list[int]]):
    rev = defaultdict(list)
    # ensure all nodes appear
    for v in graph:
        rev[v]
    for v, outs in graph.items():
        for w in outs:
            rev[w].append(v)
    return dict(rev)

def kosaraju_scc_iterative(graph: dict[int, list[int]]):
    visited = set()
    order = []

    # first pass: finishing order (iterative DFS with explicit state)
    for start in graph.keys():
        if start in visited:
            continue

        stack = [(start, 0)]
        visited.add(start)

        while stack:
            v, i = stack[-1]
            neigh = graph.get(v, [])

            if i < len(neigh):
                w = neigh[i]
                stack[-1] = (v, i + 1)
                if w not in visited:
                    visited.add(w)
                    stack.append((w, 0))
            else:
                stack.pop()
                order.append(v)

    # reverse graph
    rev = build_reverse_graph(graph)

    # second pass: collect SCCs on reversed graph
    visited.clear()
    sccs = []

    for start in reversed(order):
        if start in visited:
            continue

        comp = []
        stack = [start]
        visited.add(start)

        while stack:
            v = stack.pop()
            comp.append(v)
            for w in rev.get(v, []):
                if w not in visited:
                    visited.add(w)
                    stack.append(w)

        sccs.append(comp)

    return sccs


# ---------------------------
# 3) Naive SCC via reachability (Baseline, small subgraph)
# ---------------------------
def naive_scc_via_reachability(graph: dict[int, list[int]], limit_nodes: int = 1500):
    nodes = list(graph.keys())[:limit_nodes]
    node_set = set(nodes)

    rev = defaultdict(list)
    for v in nodes:
        for w in graph.get(v, []):
            if w in node_set:
                rev[w].append(v)

    def dfs(start, g):
        seen = set()
        st = [start]
        while st:
            v = st.pop()
            if v in seen:
                continue
            seen.add(v)
            for w in g.get(v, []):
                if w in node_set:
                    st.append(w)
        return seen

    assigned = set()
    comps = []
    for v in nodes:
        if v in assigned:
            continue
        fwd = dfs(v, graph)
        bwd = dfs(v, rev)
        comp = list((fwd & bwd) - assigned)
        for x in comp:
            assigned.add(x)
        if comp:
            comps.append(comp)

    return comps


# ---------------------------
# Utils
# ---------------------------
def measure(fn, *args, **kwargs):
    t0 = time.perf_counter()
    res = fn(*args, **kwargs)
    dt = (time.perf_counter() - t0) * 1000
    return res, dt

def summarize_sccs(sccs):
    sizes = sorted((len(c) for c in sccs), reverse=True)
    return {
        "num_scc": len(sccs),
        "largest": sizes[0] if sizes else 0,
        "top5": sizes[:5]
    }


if __name__ == "__main__":
    with open(GRAPH_IN, "rb") as f:
        data = pickle.load(f)

    graph = data["graph"]
    V = data["V"]
    E = data["E"]
    print(f"Loaded graph: V={V}, E={E}")

    scc_t, t_tarjan = measure(tarjan_scc_iterative, graph)
    sum_t = summarize_sccs(scc_t)

    scc_k, t_kos = measure(kosaraju_scc_iterative, graph)
    sum_k = summarize_sccs(scc_k)

    scc_n, t_naive = measure(naive_scc_via_reachability, graph, 1500)
    sum_n = summarize_sccs(scc_n)

    print("\n=== SCC COMPARISON ===")
    print(f"Tarjan (iter):   time_ms={t_tarjan:.2f}  summary={sum_t}")
    print(f"Kosaraju (iter): time_ms={t_kos:.2f}  summary={sum_k}")
    print(f"Naive (1500):    time_ms={t_naive:.2f}  summary={sum_n}")

    # sanity check: Tarjan & Kosaraju should agree in SCC counts/sizes (on same node set)
    if sum_t["num_scc"] != sum_k["num_scc"] or sum_t["top5"] != sum_k["top5"]:
        print("\n[WARN] Tarjan and Kosaraju summaries differ (check graph node-set consistency).")