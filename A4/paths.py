import networkx as nx
import math
import matplotlib.pyplot as plt
import heapq

ALUMNI = {
    "Harry Potter" : "BC",
    "Hermoine Granger" : "ON",
    "Ron Weasley" : "QC",
    "Luna Lovegood" : "NL", 
    "Neville Longbottom" : "SK",
    "Ginny Weasley": "NS"
}

VERTICES = [
    "Ottawa",
    "AB",
    "BC",
    "SK",
    "NS",
    "ON",
    "QC",
    "NL"
]

EDGES = [
    ("BC", "SK", {"Hops": 13, "Distance": 1800, "Time": 19, "Dementors": 6}),
    ("AB", "QC", {"Hops": 3, "Distance": 2000, "Time": 21, "Dementors": 7}),
    ("ON", "NS", {"Hops": 2, "Distance": 1300, "Time": 13, "Dementors": 4}),
    ("QC", "NL", {"Hops": 13, "Distance": 1900, "Time": 20, "Dementors": 26}),
    ("NS", "SK", {"Hops": 2, "Distance": 1800, "Time": 18, "Dementors": 5}),
    ("AB", "SK", {"Hops": 6, "Distance": 1600, "Time": 8, "Dementors": 3}),
    ("NL", "AB", {"Hops": 4, "Distance": 2400, "Time": 24, "Dementors": 9}),
    ("ON", "QC", {"Hops": 10, "Distance": 500, "Time": 5, "Dementors": 1}),
    ("NS", "ON", {"Hops": 3, "Distance": 2000, "Time": 21, "Dementors": 7}),
    ("SK", "NS", {"Hops": 3, "Distance": 2000, "Time": 20, "Dementors": 37}),
    ("QC", "SK", {"Hops": 4, "Distance": 200, "Time": 2, "Dementors": 0}),
    ("AB", "Ottawa", {"Hops": 3, "Distance": 2400, "Time": 24, "Dementors": 9}),
    ("SK", "QC", {"Hops": 2, "Distance": 2000, "Time": 20, "Dementors": 6}),
    ("ON", "AB", {"Hops": 2, "Distance": 1500, "Time": 16, "Dementors": 4}),
    ("BC", "SK", {"Hops": 2, "Distance": 1200, "Time": 14, "Dementors": 3}),
    ("NL", "QC", {"Hops": 3, "Distance": 2200, "Time": 22, "Dementors": 7}),
    ("NS", "NL", {"Hops": 10, "Distance": 1200, "Time": 12, "Dementors": 6}),
    ("QC", "Ottawa", {"Hops": 29, "Distance": 1800, "Time": 19, "Dementors": 17}),
    ("AB", "BC", {"Hops": 2, "Distance": 1800, "Time": 18, "Dementors": 27}),
    ("BC", "QC", {"Hops": 2, "Distance": 1900, "Time": 19, "Dementors": 7}),
    ("ON", "NL", {"Hops": 3, "Distance": 2300, "Time": 23, "Dementors": 8}),
    ("NS", "AB", {"Hops": 3, "Distance": 2200, "Time": 22, "Dementors": 8}),
    ("NL", "AB", {"Hops": 3, "Distance": 2300, "Time": 23, "Dementors": 8}),
    ("AB", "NL", {"Hops": 3, "Distance": 2400, "Time": 24, "Dementors": 9}),
    ("SK", "BC", {"Hops": 3, "Distance": 2000, "Time": 21, "Dementors": 8}),
    ("ON", "SK", {"Hops": 2, "Distance": 1600, "Time": 16, "Dementors": 5}),
    ("QC", "NS", {"Hops": 2, "Distance": 1000, "Time": 10, "Dementors": 2}),
    ("NL", "SK", {"Hops": 4, "Distance": 2200, "Time": 23, "Dementors": 19}),
    ("NS", "QC", {"Hops": 2, "Distance": 1100, "Time": 11, "Dementors": 2}),
    ("BC", "NL", {"Hops": 4, "Distance": 2500, "Time": 26, "Dementors": 10}),
    ("ON", "Ottawa", {"Hops": 7, "Distance": 1450, "Time": 4, "Dementors": 12}),
    ("AB", "SK", {"Hops": 5, "Distance": 600, "Time": 8, "Dementors": 3}),
    ("QC", "AB", {"Hops": 2, "Distance": 1700, "Time": 17, "Dementors": 6}),
    ("SK", "NS", {"Hops": 9, "Distance": 1800, "Time": 18, "Dementors": 5}),
    ("AB", "QC", {"Hops": 6, "Distance": 2000, "Time": 21, "Dementors": 6}),
    ("NS", "BC", {"Hops": 4, "Distance": 2500, "Time": 26, "Dementors": 10}),
    ("ON", "NS", {"Hops": 12, "Distance": 1300, "Time": 13, "Dementors": 4}),
    ("BC", "SK", {"Hops": 13, "Distance": 1800, "Time": 19, "Dementors": 6})
]


G = nx.MultiDiGraph()
G.add_nodes_from(VERTICES)
G.add_edges_from(EDGES)

def shp(graph, start, end):
    """Returns optimal route based on fewest connections"""
    current_shortest_path = None
    min_time = math.inf

    def dfs(node, path, visited):
        nonlocal min_time, current_shortest_path
        if node == end:
            # Sum the total number of hops
            time = 0
            for (_, _, attr) in path:
                time += attr

            # If hops of current path is less than minimum hops so far...
            if time < min_time:
                current_shortest_path = path[:]
                min_time = time
                return

        # For each accessible neighbor...
        for neighbor in graph.successors(node):
            if neighbor not in visited: # If we have visited the neighbor, move on
                # Get all edges between node and neighbor
                edge_dict = graph[node][neighbor]

                # For each edge between two nodes...
                for _, edge_attr in edge_dict.items():
                    visited.add(neighbor) # Visit the neighbor
                    dfs(neighbor, path + [(node, neighbor, edge_attr["Hops"])], visited)
                    visited.remove(neighbor) # backtrack

    dfs(start, [], {start})
    return current_shortest_path

def sdp(graph, start, end):
    """Returns optimal route based on the shortest distance"""
    # To start iterative algorithm, push single item to heap
    min_heap = [(0, start, [])] # (distance, node, path) - distance to starting node is 0
    min_distances = {node: float('inf') for node in graph.nodes} # Mark every other node as unreachable
    min_distances[start] = 0 # We can reach the start node though
    visited = set()

    # Until we have no more nodes to visit
    while min_heap:
        current_distance, node, path = heapq.heappop(min_heap) # Choose smallest unprocessed node

        if node in visited:
            continue

        visited.add(node)

        # If the node we have chosen is the end node, then we can be sure we found the shortest distance
        if node == end:
            return path 

        # For each accessible neighbor...
        for neighbor in graph.successors(node):
            for edge_key in graph[node][neighbor]: # For each unique edge going to that neighbor...
                edge_attr = graph[node][neighbor][edge_key] # Get the attributes of the edge
                edge_weight = edge_attr["Distance"] # Get the distance between the two nodes from the edge attributes

                # Make the new current distance the old distance to the neigbor + distance between node and neighbor
                new_current_distance = current_distance + edge_weight 

                # If new distance is better than the shortest distance, then update it
                if new_current_distance < min_distances[neighbor]:
                    min_distances[neighbor] = new_current_distance
                    heapq.heappush(min_heap, (new_current_distance, neighbor, path + [(node, neighbor, edge_attr["Distance"])]))

def stp(graph, start, end):
    """Returns optimal route based on the shortest time"""
    current_shortest_path = None
    min_time = math.inf

    def dfs(node, path, visited):
        nonlocal min_time, current_shortest_path
        if node == end:
            # Sum the total time
            time = 0
            for (_, _, attr) in path:
                time += attr

            # If hops of current path is less than minimum hops so far...
            if time < min_time:
                current_shortest_path = path[:]
                min_time = time
                return

        # For each accessible neighbor...
        for neighbor in graph.successors(node):
            if neighbor not in visited: # If we have visited the neighbor, move on
                # Get all edges between node and neighbor
                edge_dict = graph[node][neighbor]

                # For each edge between two nodes...
                for _, edge_attr in edge_dict.items():
                    visited.add(neighbor) # Visit the neighbor
                    dfs(neighbor, path + [(node, neighbor, edge_attr["Time"])], visited)
                    visited.remove(neighbor) # backtrack

    dfs(start, [], {start})
    return current_shortest_path

def fdp(graph, start, end):
    """Returns optimal route based on the least amount of dementors encountered"""
    # To start iterative algorithm, push single item to heap
    min_heap = [(0, start, [])] # (distance, node, path) - distance to starting node is 0
    least_dementors = {node: float('inf') for node in graph.nodes} # Mark every other node as unreachable
    least_dementors[start] = 0 # We can reach the start node though
    visited = set()

    # Until we have no more nodes to visit
    while min_heap:
        current_no_dementors, node, path = heapq.heappop(min_heap) # Choose smallest unprocessed node

        if node in visited:
            continue

        visited.add(node)

        # If the node we have chosen is the end node, then we can be sure we found the shortest distance
        if node == end:
            return path 

        # For each accessible neighbor...
        for neighbor in graph.successors(node):
            for edge_key in graph[node][neighbor]: # For each unique edge going to that neighbor...
                edge_attr = graph[node][neighbor][edge_key] # Get the attributes of the edge
                edge_weight = edge_attr["Dementors"] # Get the no. dementors between the two nodes from the edge attributes

                # Make the new current distance the old distance to the neigbor + distance between node and neighbor
                new_no_dementors = current_no_dementors + edge_weight 

                # If new distance is better than the shortest distance, then update it
                if new_no_dementors < least_dementors[neighbor]:
                    least_dementors[neighbor] = new_no_dementors
                    heapq.heappush(min_heap, (new_no_dementors, neighbor, path + [(node, neighbor, edge_attr["Dementors"])]))

def draw(num):
    plt.clf()
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.savefig(f"g{num}.png")

for key, value in ALUMNI.items():
    print(f"Best SHP path for {key} is {shp(G, value, "Ottawa")}")
    print(f"Best SDP path for {key} is {sdp(G, value, "Ottawa")}")
    print(f"Best STP path for {key} is {stp(G, value, "Ottawa")}")
    print(f"Best FDP path for {key} is {fdp(G, value, "Ottawa")}")
    print()

draw(1)
draw(2)
