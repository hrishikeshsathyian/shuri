# Breadth-First Search (BFS)

#### overview 

Given a graph G = (V, E) and a distinguished source vertex s, breadth-first search explores the edges of G to discover every vertex that is reachable from s. BFS discovers the vertices in hops from the source vertex. That is, starting from s, BFS first discovers all vertices with distance 1, and then all vertices with distance 2, until it has discovered every vertex reachable from s. 

Due to this hop-by-hop nature of exploration, BFS produces a "breadth-first tree" with root s that contains all reachable vertices. For any vertex v reachable from s, the path in breadth-first tree from s to v corresponds to a shortest path from s to v in G, where the shortest path is equal to the path containing the smallest number of edges from s to v. 

Hence, BFS solves the Single Source Shortest Path problem for an **unweighted graph**, working on both directed and undirected graphs. 

<center>

![bfs-tree](bfs-tree.svg)

</center>

#### how it works

The key idea behind BFS is that it explores the graph level by level, in increasing distance from the source vertex, s. 

Starting from s, BFS first visits every vertex that can be reached in one edge. These vertices are added to a **FIFO queue**. Then for each of these vertices, we remove it from the queue and add the vertices that can be reached in one edge => these vertices are two edges away from the source vertex s. This process continues until we have discovered all vertices. 

Because the FIFO queue processes vertices in the same order that they were added, we can guarantee that all vertices at distance (1) are processed before any vertex at distance 2, and so on. 

Hence, we know that once a vertex is added to the queue, we have already found the shortest number of edges to get to it. Therefore, we mark these vertexes as visited, and ignore them if they appear as neighbours of future vertices.  

The algorithm terminates once the queue is empty.

#### psuedo-code

```text 
BFS(G, s):

    create an empty queue Q
    create a visited set                # keep track of visited vertices

    mark s as visited
    enqueue s into Q

    while Q is not empty:

        u = dequeue Q                   

        for each neighbour v of u:

            if v is not visited:
                mark v as visited
                enqueue v into Q

```
> for each level i, we have to process all vertices at level i before we start processing vertices at level i+1. Processing a vertex at level i, would only add vertices of level i+1 to the queue. Hence, we conclude that at any point of time, the queue will only contain vertexes from at most two levels. 

#### time and space complexity analysis 

Assuming the graph is represented using an **adjacency list**, BFS has a time complexity of:

$$
O(V + E)
$$

where \(V\) is the number of vertices and \(E\) is the number of edges.

Each vertex is visited at most once, giving \(O(V)\) work. When a vertex is processed, BFS iterates through its adjacency list. Across all vertices, this means every edge is examined once in a directed graph, or twice in an undirected graph, once from each endpoint. In either case, this contributes \(O(E)\).

Therefore, the total time complexity is:

$$
O(V + E)
$$

The auxiliary space complexity is:

$$
O(V)
$$

The **visited set** can contain up to \(V\) vertices, and in the worst case the **queue** can also contain up to \(V\) vertices.

If we were to consider storing the **input graph**, then it would be O(V + E) for an adjacency list and O(V²) for adjacency matrix. 

> If the graph itself is included in the space analysis, an adjacency-list representation requires \(O(V + E)\) space.
> If the graph was represented using an adjacency matrix, it would be O(V²) since for each vertex, you would have to scan its entire row of V possible neighbours


### variations 

One common variation of BFS would be to keep track of the shortest-path distances of each vertex visited. We would then need to maintain a distance map ( O(V) space ). Then each time we process a vertex u, for each of its unvisited neighbours v, we set ``` dist[v] = dist[u] + 1 ```

A similar approach applies for keeping track of parent vertexes. 

#### relevant leetcode questions 

