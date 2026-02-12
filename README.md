# advent_of_code_2025
Advent of Code challenge 2025. https://adventofcode.com/2025

---

## Day 11: Reactor — Lessons Learned

This was the best question yet. Here's what we learned:

### The Problem
- **Part I:** Count all paths from `you` to `out` in a directed graph of devices. Straightforward DFS worked fine (786 paths).
- **Part II:** Count all paths from `svr` to `out` that pass through both `dac` and `fft`. Same DFS approach ran forever.

### Why DFS Ran Forever (It Wasn't a Bug)

1. **First suspicion — infinite loop due to cycles.** The original DFS had no visited-node tracking, so if the graph had cycles (A → B → C → A), it would loop forever. We added a `visited` set to fix this.
2. **Real problem — combinatorial explosion.** Even with cycle prevention, the graph from `svr` is massively wider (some nodes have 18+ outputs). The number of valid paths is potentially in the **billions**. DFS enumerates every single path one by one — O(P) where P = number of paths. That's not an infinite loop, it's just an impossibly large finite number.

### The Fix: Dynamic Programming on a DAG

Instead of walking every path individually, we used **DP (Dynamic Programming)** on the **DAG (Directed Acyclic Graph)**:

1. **Topological Sort** — Line up all nodes so every edge points forward. This guarantees that when we process a node, all paths leading into it have already been counted.
2. **Propagate counts forward** — Start with `dp[svr] = 1`. For each node in topological order, push its count to all its neighbors. When paths merge at a node, we just add the counts together instead of tracking individual paths.
3. **Track "seen" state** — Since we need paths through both `dac` and `fft`, we track which required nodes have been visited. With 2 required nodes, there are only 4 possible states: `{}`, `{dac}`, `{fft}`, `{dac, fft}`.

### Complexity Comparison

| Approach | Time Complexity | On Our Input |
|---|---|---|
| DFS (enumerate all paths) | O(P) — P = number of paths | Billions of paths — runs forever |
| DP on DAG | O(V × S × E) — V=nodes, S=states, E=edges | ~few thousand ops — instant |

### Key Takeaways

- **DFS is efficient for graph traversal (O(V+E)), but not for counting all paths** — the number of paths can be exponential in the graph size.
- **A DAG (Directed Acyclic Graph)** is a directed graph with no cycles. This property enables topological sorting.
- **Topological sort** orders nodes so every edge points forward, ensuring DP counts are complete before being propagated.
- **DP merges paths** — if 1,000 paths arrive at node X with the same state, we store `1000` instead of tracking 1,000 separate paths. From X onward, we do the work once.
- **Richard Bellman** formalized DP in the 1950s. He named it "Dynamic Programming" because it sounded impressive enough that no politician would object to funding it.
- This pattern (DP on a DAG) shows up everywhere: shortest paths, build systems (Make/Bazel), spreadsheets, and even neural network forward passes.
