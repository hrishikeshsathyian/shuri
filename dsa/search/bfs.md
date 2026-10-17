# Breadth-First Search (BFS)

#### overview

BFS explores a graph G = (V, E) from a source vertex s, discovering vertices in order of their hop distance from s: all vertices at distance 1, then distance 2, and so on.

Because of this, the path from s to any reachable vertex v in the BFS tree is a shortest path (fewest edges). Hence BFS solves Single Source Shortest Path on an **unweighted graph**, for both directed and undirected graphs.

<center>

![bfs-tree](bfs-tree.svg)

</center>

#### how it works

BFS keeps a **FIFO queue** of discovered-but-unprocessed vertices. Dequeue a vertex u, and enqueue each unvisited neighbour of u. Since the queue preserves insertion order, every vertex at distance d is processed before any vertex at distance d + 1.

A vertex is marked visited **when it is enqueued**, not when it is dequeued. At that moment we have already found its shortest distance, so later encounters can be ignored.

At any point, the queue holds vertices from at most two adjacent levels.

#### pseudo-code

```text
BFS(G, s):
    Q = empty queue
    visited = {s}
    enqueue s into Q

    while Q is not empty:
        u = dequeue Q
        for each neighbour v of u:
            if v not in visited:
                add v to visited
                enqueue v into Q
```

#### complexity

With an adjacency list:

- **Time:** O(V + E). Each vertex is dequeued once, and each adjacency list is scanned once (every edge is seen once if directed, twice if undirected).
- **Auxiliary space:** O(V) for the visited set and the queue.
- **Input graph:** O(V + E) as an adjacency list, O(V²) as an adjacency matrix (which also makes time O(V²), since each vertex scans a full row).

#### implementation in python 

Use `collections.deque`, since `list.pop(0)` is O(n) while `deque.popleft()` is O(1).

```python
from collections import deque

def bfs(graph, s):
    """Return vertices in BFS visiting order. graph: dict[vertex, list[vertex]]"""
    visited = {s}
    dq = deque([s])
    order = []

    while dq:
        u = dq.popleft()
        order.append(u)
        for v in graph[u]:
            if v not in visited:
                visited.add(v)
                dq.append(v)

    return order
```

#### variation: tracking levels

To know which level we are on, process the queue one level at a time. At the start of each outer iteration, `len(dq)` is exactly the number of vertices in the current level, so an inner loop of that size consumes the current level while the neighbours it enqueues form the next one.

```python
from collections import deque

def bfs_levels(graph, s):
    """Return a list of levels: levels[i] = vertices at distance i from s."""
    visited = {s}
    dq = deque([s])
    levels = []

    while dq:
        level = []
        for _ in range(len(dq)):        # len(dq) is evaluated once, before the loop starts
            u = dq.popleft()
            level.append(u)
            for v in graph[u]:
                if v not in visited:
                    visited.add(v)
                    dq.append(v)
        levels.append(level)

    return levels
```
The index of each level is the shortest distance from the source, so this gives distances without a separate map. If you need the distance of a specific vertex, return early when you encounter it, with `len(levels)` as the distance. Note `range(len(dq))` is fixed up front, so vertices appended during the loop wait for the next round.

