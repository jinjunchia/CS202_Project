import sys
import random

def read_input():
    """Reads input from stdin and returns number of locations, vehicle capacity, distance matrix, and demand vector."""
    def safe_read():
        line = sys.stdin.readline().strip()
        while line == "":  # Skip empty lines
            line = sys.stdin.readline().strip()
        return line
    
    n = int(safe_read())  # Read n (number of locations)
    Q = int(safe_read())  # Read Q (vehicle capacity)

    D = []
    for _ in range(n):
        row = list(map(int, safe_read().split()))
        D.append(row)

    q = list(map(int, safe_read().split()))

    return n, Q, D, q

def compute_savings(n, D):
    savings = [(i, j, D[0][i] + D[0][j] - D[i][j]) for i in range(1, n) for j in range(i + 1, n)]
    return sorted(savings, key=lambda x: x[2], reverse=True)

def clarke_wright_savings(n, Q, D, q):
    savings = compute_savings(n, D)
    routes = {i: [0, i, 0] for i in range(1, n)}
    route_loads = {i: q[i] for i in range(1, n)}

    parent = {i: i for i in range(1, n)}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union(u, v):
        parent[find(v)] = find(u)

    for i, j, _ in savings:
        ri, rj = find(i), find(j)
        if ri != rj:
            route_i, route_j = routes[ri], routes[rj]
            load_i, load_j = route_loads[ri], route_loads[rj]
            total_load = load_i + load_j
            if total_load > Q:
                continue
            if route_i[-2] == i and route_j[1] == j:
                new_route = route_i[:-1] + route_j[1:]
            elif route_j[-2] == j and route_i[1] == i:
                new_route = route_j[:-1] + route_i[1:]
            else:
                continue

            new_id = min(ri, rj)
            routes[new_id] = new_route
            route_loads[new_id] = total_load
            for node in new_route[1:-1]:
                parent[node] = new_id
                routes[node] = new_route
                route_loads[node] = total_load

    # Extract unique routes
    seen = set()
    final_routes = []
    for r in routes.values():
        tid = tuple(r)
        if tid not in seen:
            seen.add(tid)
            final_routes.append(r)
    return final_routes

def total_distance(routes, D):
    return sum(D[route[i]][route[i+1]] for route in routes for i in range(len(route)-1))

def main():
    n, Q, D, q = read_input()
    routes = clarke_wright_savings(n, Q, D, q)
    for route in routes:
        print(" ".join(map(str, route)))

if __name__ == "__main__":
    main()