import sys
import random

def load_cvrp_data(filename):
    with open(filename, 'r') as f:
        n = int(f.readline().strip())  # Number of locations
        Q = int(f.readline().strip())  # Vehicle capacity
        
        D = [list(map(int, f.readline().strip().split())) for _ in range(n)]
        q = list(map(int, f.readline().strip().split()))
    
    return n, Q, D, q

def compute_savings(n, D):
    savings = []
    for i in range(1, n):
        for j in range(i + 1, n):
            savings.append((i, j, D[0][i] + D[0][j] - D[i][j]))
    savings.sort(key=lambda x: x[2], reverse=True)
    return savings

def clarke_wright_savings(n, Q, D, q):
    savings = compute_savings(n, D)
    routes = {i: [0, i, 0] for i in range(1, n)}  # Each node starts as its own route
    route_loads = {i: q[i] for i in range(1, n)}
    
    for i, j, _ in savings:
        if i in routes and j in routes and routes[i] != routes[j]:
            route_i, route_j = routes[i], routes[j]
            
            # Ensure capacity constraint is met
            total_load = sum(q[node] for node in route_i[1:-1]) + sum(q[node] for node in route_j[1:-1])
            if total_load > Q:
                continue  # Do not merge if it exceeds capacity
                
            if route_i[-2] == i and route_j[1] == j:
                new_route = route_i[:-1] + route_j[1:]
            elif route_j[-2] == j and route_i[1] == i:
                new_route = route_j[:-1] + route_i[1:]
            else:
                continue
            
            for node in new_route[1:-1]:
                routes[node] = new_route
            
    # Split routes correctly if they exceed vehicle capacity
    final_routes = []
    for route in set(tuple(r) for r in routes.values()):
        split_route = [0]
        load = 0
        for node in route[1:-1]:
            if load + q[node] > Q:
                split_route.append(0)
                final_routes.append(split_route)
                split_route = [0]
                load = 0
            split_route.append(node)
            load += q[node]
        split_route.append(0)
        final_routes.append(split_route)
    
    return final_routes

def two_opt(route, D):
    best_distance = sum(D[route[i]][route[i+1]] for i in range(len(route)-1))
    improved = True
    
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 2, len(route) - 1):
                new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
                new_distance = sum(D[new_route[k]][new_route[k+1]] for k in range(len(new_route)-1))
                if new_distance < best_distance:
                    route[i:j+1] = reversed(route[i:j+1])
                    best_distance = new_distance
                    improved = True
    
    return route

def optimize_routes(routes, D):
    return [two_opt(route, D) for route in routes]

def main():
    filename = "6.in"
    n, Q, D, q = load_cvrp_data(filename)
    initial_routes = clarke_wright_savings(n, Q, D, q)
    optimized_routes = optimize_routes(initial_routes, D)
    
    for route in optimized_routes:
        print(" ".join(map(str, route)))

if __name__ == "__main__":
    main()