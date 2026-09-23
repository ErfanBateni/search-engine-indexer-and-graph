# search-engine-indexer-and-graph
Scalable Search Engine Implementation: Text parsing, Inverted Indexing, Compression, and Web Graph SCC Analysis using Python

# Scalable Search Engine & Web Graph Analyzer

This project implements a scalable search engine capable of processing, indexing, and analyzing massive datasets (e.g., Wikipedia dumps). It addresses real-world challenges in data streams, inverted index compression, query optimization, and directed graph analysis, developed as the final project for the **Data Structures & Algorithms** course.

---

## 📌 Project Overview
The primary goal is to build an end-to-end search architecture with strict memory constraints. Instead of loading monolithic data into RAM, this implementation utilizes stream processing, efficient data structures, index compression techniques, and web-graph modeling.

---

## ⚙️ Architecture & Sprints Implementation

### Sprint 1: Data Parsing & Stream Processing
*   **Challenge:** Processing gigabytes of nested, semi-structured XML/SQL dumps without exceeding memory limits.
*   **Solution:** Implemented iterative parsing and streaming techniques to extract structural metadata and document text. Raw data was efficiently converted into flattened, manageable records (e.g., `jsonl`).

### Sprint 2: Deduplication & Memory Trade-offs
*   **Challenge:** Identifying duplicate content within a massive dataset under strict memory constraints.
*   **Solution:** Evaluated three distinct approaches:
    1.  *Exact String Matching (Sets):* High accuracy, high memory consumption.
    2.  *Hashing:* Reduced memory footprint, balanced performance.
    3.  *Probabilistic Data Structures:* Extremely low memory footprint with approximate accuracy.

### Sprint 3: Inverted Index & Compression
*   **Challenge:** Building a searchable index and optimizing it for both lookup speed and storage size.
*   **Solution:** 
    *   Developed a raw **Inverted Index** using Hash Maps (Dictionaries) for $O(1)$ keyword lookup.
    *   Implemented **Delta Encoding (Gap Compression)** for document ID posting lists. This significantly reduced storage requirements by encoding the small intervals between ordered IDs rather than the large IDs themselves, showcasing a standard industry compression technique.

### Sprint 4: Advanced Analytical Queries
*   **Challenge:** Supporting complex queries efficiently on large-scale data.
*   **Solution:** 
    *   **Range Queries:** Implemented Binary Search over sorted arrays, outperforming linear search and proving more practical than complex balanced tree implementations.
    *   **Top-K Retrieval:** Utilized a **Min-Heap (Priority Queue)** to extract the most relevant results in $O(N \log K)$ time, minimizing both time and space complexity without fully sorting the dataset.

### Sprint 5: Web Graph Construction & SCC Analysis
*   **Challenge:** Modeling document relationships to understand macro-level data structures (similar to PageRank foundations).
*   **Solution:**
    *   Parsed document hyperlinks to construct a massive directed graph (e.g., 10,000 nodes, 65,000 edges).
    *   Analyzed the graph to find **Strongly Connected Components (SCC)**.
    *   Implemented both **Tarjan’s** and **Kosaraju’s** algorithms (linear time complexity $O(V+E)$), successfully identifying the main structural core of the web graph.

---

## 🛠️ Tools & Technologies
*   **Language:** Python (Stream Processing, Data Structures)
*   **Algorithms:** Tarjan's/Kosaraju's SCC, Binary Search, Heaps, Delta Compression, Hashing

---

## 📂 Repository Structure
*   `/src`: Contains all Python scripts modularized by sprint (e.g., parsing, indexing, queries, graph analysis).
*   `DS_Report_Erfan_Bateni_400100792.pdf`: Detailed analytical project report containing performance benchmarks, memory vs. time trade-offs, and architectural decisions.

*(Note: Raw dataset dumps and compiled binary indexes `.pkl` / `.bin` are excluded from this repository due to size constraints. Please refer to the PDF report for benchmark outputs).*
