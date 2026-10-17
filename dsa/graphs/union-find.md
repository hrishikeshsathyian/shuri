# Union-Find

#### overview

Union-Find maintains a collection of **disjoint sets** and supports two operations:

- `find(x)`: return the representative (root) of the set containing x.
- `union(x, y)`: merge the sets containing x and y.

Two elements are in the same set **iff** `find(x) == find(y)`.

It answers "are these two things connected?" and "how many groups are there?" quickly, especially when connections arrive **incrementally** (edges added one at a time) and you query in between.

#### core idea

Represent each set as a tree stored in a `parent` array. Each element points to its parent; the root points to itself.

```text
parent = [0, 0, 1, 3, 3]

    0        3
   /        /
  1        4
 /
2          sets: {0,1,2} and {3,4}
```

- `find(x)`: follow parent pointers until you reach a node whose parent is itself.
- `union(x, y)`: find both roots; if they differ, make one root point to the other.

Naive trees can degenerate into a chain, making `find` O(n). Two optimizations fix that.

#### the two optimizations

**1. Path compression** (in `find`): flatten the tree while climbing so future finds are shorter. There are two common flavours:

- *Full compression:* every node on the path is repointed directly at the root (recursive version below).
- *Path halving:* each node is repointed at its **grandparent** as you climb (the iterative version in the class below). One pass, no recursion, and the same amortized bound.

**2. Union by size (or rank)**: always attach the smaller tree under the larger one, so trees stay shallow.

#### implementation (Python)

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))   # each node starts as its own root
        self.size = [1] * n            # size of the tree rooted at each root
        self.components = n            # number of disjoint sets

    def find(self, x):
        # iterative, path halving
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False               # already connected: this edge forms a cycle
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx            # rx is the larger root
        self.parent[ry] = rx
        self.size[rx] += self.size[ry]
        self.components -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)
```

Recursive `find` with full path compression (a drop-in replacement):

```python
def find(self, x):
    if self.parent[x] != x:
        self.parent[x] = self.find(self.parent[x])   # parent[x] = the ROOT
    return self.parent[x]
```

Notes:

- `union` returns `True` if it merged two sets and `False` if they were already joined. This boolean powers cycle detection (Redundant Connection, Graph Valid Tree, Kruskal).
- `components` is decremented only on a real merge.
- The recursive `find` can hit Python's recursion limit (~1000) on deep chains, but union by size keeps trees shallow enough that this is rarely a problem in practice.

Quick example:

```python
uf = UnionFind(5)
uf.union(0, 1)
uf.union(1, 2)
uf.union(3, 4)
uf.connected(0, 2)   # True
uf.connected(2, 3)   # False
uf.components        # 2
uf.union(0, 2)       # False, already connected
```

#### time and space complexity

| Operation | Amortized time |
|-----------|----------------|
| `find`    | O(α(n)) |
| `union`   | O(α(n)) |
| init (the constructor `UnionFind(n)`) | O(n) |

The init row is only the setup: `list(range(n))` and `[1] * n` each create n entries, and no unions have happened yet. The cost of the actual work comes after, in the `find` / `union` calls.

- **m operations on n elements:** O(m · α(n)). Space: O(n).
- α is the inverse Ackermann function, which grows so slowly that α(n) ≤ 4 for any n you will ever meet. In practice, treat it as O(1). Strictly speaking it is not constant, since it grows without bound, just absurdly slowly, so over E edges the total is O(E · α(V)), which is *effectively* O(E).

> ### The bound is AMORTIZED, not per-operation
>
> **A single `find` or `union` can still be slow.** If it lands on a tall tree, that one call may take O(log n) (or worse without the optimizations). The O(α(n)) figure is a guarantee on the **total cost of a whole sequence of operations**, divided by the number of operations: the expensive call flattens the tree as it climbs, so the calls that follow are cheap.

#### why the optimizations matter

`find(x)` costs as many steps as x is deep in its tree, so everything comes down to **how tall the trees get**. Each optimization attacks that in a different way:

| Setup | Cost per `find` / `union` | Kind of bound |
|-------|---------------------------|---------------|
| neither optimization | O(n) | worst case, per call |
| union by size only | O(log n) | worst case, per call |
| path compression only | O(log n) | amortized |
| both | O(α(n)) | amortized |

Why each row is what it is:

- **Neither: O(n).** The unions can build a chain. For example, if `union(0,1)`, `union(1,2)`, `union(2,3)`, ... each hang the first root under the second, you get `0 → 1 → 2 → ... → n-1`. Each of those unions is cheap, but then `find(0)` has to walk all n nodes.
- **Union by size only: O(log n).** A node only gets deeper when its tree is attached under a tree that is at least as big, which means its tree's size at least doubles. A size can double at most log₂ n times, so no node is ever deeper than log₂ n. This is a hard per-call guarantee.
- **Path compression only: O(log n) amortized.** There is no height guarantee, so one `find` can still be O(n), but it flattens the path as it goes. Over any sequence of calls, the total cost works out to O(log n) per call, amortized.
- **Both: O(α(n)) amortized.** Union by size keeps trees short to begin with, and path compression flattens whatever height is left. Together they give the near-constant bound.

Note the last column: the first two rows are **worst-case** guarantees and the last two are **amortized**. That is the same worst-case vs amortized distinction as in the callout above.

For interviews, either optimization alone is acceptable, but writing both is the standard.

#### patterns and templates

**Pattern 1: count components.** Union every edge, return `uf.components`.

```python
def countComponents(n, edges):
    uf = UnionFind(n)
    for a, b in edges:
        uf.union(a, b)
    return uf.components
```

**Pattern 2: detect a cycle / redundant edge.** The first edge where `union` returns `False` is the one that closes a cycle.

```python
def findRedundantConnection(edges):
    uf = UnionFind(len(edges) + 1)     # nodes are 1-indexed
    for a, b in edges:
        if not uf.union(a, b):
            return [a, b]
```

**Pattern 3: valid tree.** A graph of n nodes is a tree iff it has exactly n - 1 edges **and** no edge closes a cycle (equivalently, it ends with 1 component).

```python
def validTree(n, edges):
    if len(edges) != n - 1:
        return False
    uf = UnionFind(n)
    return all(uf.union(a, b) for a, b in edges)
```

**Pattern 4: map non-integer or 2D keys to indices.** Flatten a grid cell to `r * cols + c`, or use a dict-based union-find for strings and arbitrary hashables.

```python
class DictUnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx != ry:
            self.parent[ry] = rx
```

**Pattern 5: group elements by root.** After all unions, bucket elements by `find(x)`.

```python
from collections import defaultdict

groups = defaultdict(list)
for x in range(n):
    groups[uf.find(x)].append(x)
```

`
