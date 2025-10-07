import heapq

def dijkstra(graph, start, end):
    pq = [(0, start, [start])]   # (distance, node, path)
    visited = set()

    while pq:
        (dist, current, path) = heapq.heappop(pq)

        if current in visited:
            continue
        visited.add(current)

        if current == end:
            return dist, path

        for neighbor, weight in graph.get(current, []):
            if neighbor not in visited:
                heapq.heappush(pq, (dist + weight, neighbor, path + [neighbor]))

    return float("inf"), []  # No path found


# ---- MAIN PROGRAM ----
graph = {}
print("=== Dijkstra’s Shortest Path Finder ===")

edges = int(input("Enter number of edges: "))

for _ in range(edges):
    u, v, w = input("Enter edge (node1 node2 weight): ").split()
    w = int(w)
    graph.setdefault(u, []).append((v, w))
    graph.setdefault(v, []).append((u, w))  # remove this line if directed graph

source = input("Enter source node: ")
target = input("Enter destination node: ")

# Run Dijkstra
distance, path = dijkstra(graph, source, target)

# Display results
if path:
    print(f"\nShortest path from {source} to {target}: {' -> '.join(path)}")
    print(f"Total weight: {distance}")
else:
    print(f"\nNo path exists between {source} and {target}.")
