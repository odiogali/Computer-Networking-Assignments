# Hogwarts Alumni Pathfinding Algorithms Report

This report explains the algorithms SHP, SDP, FDP, and STP used to compute optimal paths for Hogwarts alumni to reach Ottawa. Each algorithm optimizes a different criterion: number of hops, distance, dementors, or time.

---

## 1. SHP: **Shortest Hops Path**

### Algorithm:
A **Depth-First Search (DFS)** is used to exhaustively explore all possible paths, tracking the one with the fewest number of hops.

#### Step-by-Step Breakdown:
1. Start at the source node with an empty path.
2. Recursively explore each unvisited neighbor node.
3. For each complete path reaching the destination:
   - Count the number of hops (edges).
   - If it’s less than the minimum so far, record it as the best path.
4. Backtrack to explore alternative paths.

### Time Complexity:
- The algorithm explores all possible paths from start to finish without pruning of any sort; in the worst case, this version of DFS can still visit the same node multiple times through different paths
	- Most importantly, in the backtracking step, we remove the node from the visited set after exploring it, allowing it to be revisited along a different path
	- For each node, the function explores all its accessible neighbors and for each neighbor, it explores all edges connected to it
- **O(V^E)** since we have generally have E choices at each node - assuming that E is the number of outgoing edges from a node - and the path can have up to V nodes
	- This exponential complexity arises because:
		- The algorithm explores all possible paths from start to end
		- Each node can be visited multiple times through different paths due to the backtracking mechanism
		- In the worst case, the path can include up to V nodes, and at each step, there are potentially many choices of edges to follow


### Challenges:
- DFS does not guarantee the shortest path by default, requiring manual comparison.
- I needed to do a lot of testing to ensure that backtracking was working properly.
- Tracking the fewest hops requires evaluating all potential paths and I couldn't think of a reasonable way to prune the evaluation.
- Multi-edges require managing different weights and connections per path.

### Result Explanation:
Returns the path from the start to Ottawa with the fewest number of hops, using DFS which explicitly computes and compares all candidates.

---

## 2. SDP: **Shortest Distance Path**

### Algorithm:
An optimized **Dijkstra's Algorithm** is used with a priority queue (min-heap). Nodes are selected based on the least cumulative distance from the start.

#### Step-by-Step Breakdown:
1. Initialize all node distances to infinity, and the start node to 0.
2. Push the start node onto the priority queue.
3. While the queue is not empty:
   - Pop the node with the smallest cumulative distance.
   - For each neighbor, calculate the distance through the current node.
   - If it's smaller than the previously recorded distance, update it and push it to the queue.

### Time Complexity:
- **O((V + E) log V)** since the algorithm uses a min-heap for the priority queue for which insertions and deletions tend to be logarithmic.

### Challenges:
- Ensuring all distances are correctly updated in the presence of multi-edges; for the longest time I just couldn't figure out how to handle multiple edges between two nodes
- I also struggled with accurately handling the edge weights (distance) when they vary between connections - like when an edge between two nodes had different weights in the two directions

### Result Explanation:
The path with the least total kilometers from start to Ottawa is returned.

---

## 3. STP: **Shortest Time Path**

### Algorithm:

The Shortest Time Path (STP) algorithm implements an exhaustive Depth-First Search (DFS) approach to find the path with the minimum total time between specified start and end nodes in a directed graph. Unlike traditional DFS that simply explores all reachable nodes, this implementation tracks the cumulative time along each possible path and retains only the path with the minimum total time.

#### Step-by-Step Breakdown:

1. The algorithm begins a recursive DFS from the start node, maintaining a set of visited nodes to avoid cycles
2. For each node, it explores all unvisited neighboring nodes and all possible edges connecting to them
3. When the end node is reached, it calculates the total time of the current path
4. If this time is less than the minimum time found so far, it updates the current shortest path
5. The algorithm uses backtracking by removing nodes from the visited set after exploring them, allowing nodes to be revisited through different paths
6. This exhaustive search continues until all possible paths have been explored

### Time Complexity:

The time complexity of this algorithm is **O(V^E)**.

### Challenges:

1. **Backtracking Implementation**: Correctly implementing the backtracking mechanism (adding and removing nodes from the visited set) to ensure all possible paths are explored
2. **Multiple Edges Between Nodes**: Managing cases where multiple edges exist between the same pair of nodes, each with different time values

### Result Explanation:

The algorithm returns the optimal path from start to end based on the cumulative time, represented as a list of tuples. Each tuple contains:

- The source node
- The destination node
- The time value associated with that edge

If no path exists between the start and end nodes, the function will return `None`. The path returned is guaranteed to be the one with the minimum total time among all possible paths between the start and end nodes, making it optimal in terms of travel time.

---
## 4. FDP: **Fewest Dementors Path**

### Algorithm:
A modified **Dijkstra's Algorithm** is used. Instead of distance, it tracks the fewest cumulative dementors encountered.

#### Step-by-Step Breakdown:
1. Initialize all node dementor counts to infinity; set the start node to 0.
2. Push the start node onto the priority queue.
3. While the queue is not empty:
   - Pop the node with the smallest cumulative dementor count.
   - For each neighbor, compute the total dementors if this path is taken.
   - If it's lower than the recorded count, update and push it.

### Time Complexity:
- **O((V + E) log V)** with a priority queue.

### Challenges:
- Multi-edges may have different dementor values, requiring careful comparison.
- Updating and tracking optimal paths with respect to a custom attribute (dementors).

### Result Explanation:
Returns the path (list of tuples containing the edge information along the path taken) from the start to Ottawa with the fewest total dementor encounters.

---

## Summary Table

| Algorithm | Criterion Optimized | Path-Finding Technique | Cost Metric       |
| --------- | ------------------- | ---------------------- | ----------------- |
| SHP       | Number of hops      | Depth-First Search     | Hops              |
| SDP       | Distance            | Dijkstra's Algorithm   | Distance (km)     |
| STP       | Time                | Depth-First Search     | Travel time (hrs) |
| FDP       | Dementors           | Dijkstra's Algorithm   | Dementor count    |

---

## Observations
- **DFS and Dijkstra's algorithms** offer distinct strengths for pathfinding, depending on the cost metric.
- **MultiDiGraph** structure supports different edge weights, which is crucial for customized criteria like time or dementors.
- **Dijkstra’s algorithm variants** allow flexibility by simply changing the cost metric (distance, time, or dementors).

---

## Conclusion
Each algorithm suits different optimization goals. Depending on whether minimizing time, distance, hops, or danger (dementors), different strategies provide optimal paths. By using DFS for hop count and Dijkstra’s algorithm for weighted metrics, the solution remains both accurate and efficient for magical transportation planning.

