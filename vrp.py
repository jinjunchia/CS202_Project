import sys
import heapq

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

def clarke_wright_savings(n, Q, D, q):
    """Optimized Clarke-Wright Savings Algorithm for CVRP."""
    customers = set(range(1, n))
    routes = {i: [0, i, 0] for i in customers}
    route_demand = {i: q[i] for i in customers}

    # Compute savings and use a priority queue for fast sorting
    savings = []
    for i in customers:
        for j in customers:
            if i < j:
                saving = D[i][0] + D[0][j] - D[i][j]
                heapq.heappush(savings, (-saving, i, j))  # Store as negative to simulate max-heap

    while savings:
        _, i, j = heapq.heappop(savings)  # Extract best saving pair
        
        if i in routes and j in routes and routes[i] != routes[j]:
            route_i, route_j = routes[i], routes[j]
            new_demand = route_demand[i] + route_demand[j]

            if new_demand <= Q:
                # Merge only at endpoints
                if route_i[-2] == i and route_j[1] == j:
                    merged_route = route_i[:-1] + route_j[1:]
                elif route_j[-2] == j and route_i[1] == i:
                    merged_route = route_j[:-1] + route_i[1:]
                else:
                    continue  # Skip merge if it doesn't maintain a valid order

                # Update merged route
                for k in merged_route:
                    if k != 0:
                        routes[k] = merged_route

                route_demand[i] = new_demand
                route_demand[j] = new_demand
                del routes[i]
                del routes[j]

    return list(routes.values())

def repair_routes(routes, n, Q, D, q):
    """Ensure all customers are assigned to a valid route."""
    all_customers = set(range(1, n))
    visited_customers = {node for route in routes for node in route if node != 0}
    missing_customers = all_customers - visited_customers

    if missing_customers:
        for customer in missing_customers:
            best_route = None
            best_cost = float('inf')

            for route in routes:
                if sum(q[i] for i in route if i != 0) + q[customer] <= Q:
                    for idx in range(1, len(route)):
                        new_route = route[:idx] + [customer] + route[idx:]
                        new_cost = sum(D[new_route[i]][new_route[i+1]] for i in range(len(new_route)-1))

                        if new_cost < best_cost:
                            best_cost = new_cost
                            best_route = (route, idx, customer)

            if best_route:
                route, idx, customer = best_route
                route.insert(idx, customer)
            else:
                routes.append([0, customer, 0])  # Create a new route

    return routes

def check(routes, n, Q, q):
    """Checks if all customers are visited exactly once and if routes respect capacity constraints."""
    visited = set()
    capacity_violations = False

    for route in routes:
        total_demand = sum(q[i] for i in route if i != 0)
        if total_demand > Q:
            #print(f"ERROR: Route {route} exceeds capacity ({total_demand} > {Q})")
            capacity_violations = True

        for node in route:
            if node != 0:
                if node in visited:
                    #print(f"ERROR: Customer {node} visited multiple times!")
                    return False
                visited.add(node)

    expected_customers = set(range(1, n))
    missing_customers = expected_customers - visited

    if missing_customers:
        #print(f"ERROR: Missing customers: {missing_customers}")
        return False

    return not capacity_violations

def solve_cvrp(n, Q, D, q):
    """Clarke-Wright Savings + Repair Step for CVRP."""
    #print("DEBUG: Running Clarke-Wright Savings...")
    routes = clarke_wright_savings(n, Q, D, q)

    #print("DEBUG: Repairing routes if necessary...")
    routes = repair_routes(routes, n, Q, D, q)

    #print(f"DEBUG: Final routes count: {len(routes)}")
    return routes

def main():
    #print("Reading input...")
    n, Q, D, q = read_input()

    #print(f"Number of locations: {n}, Vehicle Capacity: {Q}")
    #print("Solving CVRP...")

    routes = solve_cvrp(n, Q, D, q)

    #print("Checking solution validity...")
    if check(routes, n, Q, q):
        #print("Solution is valid. Printing routes:")
        for route in routes:
            print(" ".join(map(str, route)))
    # else:
    #     print("Invalid solution! Some customers are missing or constraints are violated.")

if __name__ == "__main__":
    main()


# import sys
# import heapq
# import random

# def read_input():
#     """Reads input from stdin and returns number of locations, vehicle capacity, distance matrix, and demand vector."""
#     def safe_read():
#         line = sys.stdin.readline().strip()
#         while line == "":
#             line = sys.stdin.readline().strip()
#         return line
    
#     n = int(safe_read())  # Read n (number of locations)
#     Q = int(safe_read())  # Read Q (vehicle capacity)

#     D = []
#     for _ in range(n):
#         row = list(map(int, safe_read().split()))
#         D.append(row)

#     q = list(map(int, safe_read().split()))

#     return n, Q, D, q

# def compute_savings(n, D, q):
#     """Compute the savings list using demand-aware prioritization."""
#     savings = []
#     for i in range(1, n):
#         for j in range(i + 1, n):
#             saving = (D[i][0] + D[0][j] - D[i][j]) / ((q[i] + q[j]) ** 0.8)  
#             heapq.heappush(savings, (-saving, i, j))  
#     return savings

# def clarke_wright_savings(n, Q, D, q):
#     """Improved Clarke-Wright Savings Algorithm for CVRP."""
#     customers = set(range(1, n))
#     routes = {i: [0, i, 0] for i in customers}
#     route_demand = {i: q[i] for i in customers}

#     savings = compute_savings(n, D, q)

#     while savings:
#         _, i, j = heapq.heappop(savings)

#         if i in routes and j in routes and routes[i] != routes[j]:
#             route_i, route_j = routes[i], routes[j]
#             new_demand = route_demand[i] + route_demand[j]

#             if new_demand <= Q:
#                 if route_i[-2] == i and route_j[1] == j:
#                     merged_route = route_i[:-1] + route_j[1:]
#                 elif route_j[-2] == j and route_i[1] == i:
#                     merged_route = route_j[:-1] + route_i[1:]
#                 else:
#                     continue  

#                 for k in merged_route:
#                     if k != 0:
#                         routes[k] = merged_route

#                 route_demand[i] = new_demand
#                 route_demand[j] = new_demand
#                 del routes[i]
#                 del routes[j]

#     return list(routes.values())

# def two_opt(route, D):
#     """Applies 2-opt optimization to reduce total distance."""
#     best_route = route[:]
#     best_cost = sum(D[best_route[i]][best_route[i+1]] for i in range(len(best_route)-1))

#     for i in range(1, len(route) - 2):
#         for j in range(i + 1, len(route) - 1):
#             new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
#             new_cost = sum(D[new_route[k]][new_route[k+1]] for k in range(len(new_route)-1))

#             if new_cost < best_cost:
#                 best_route = new_route
#                 best_cost = new_cost

#     return best_route

# def swap_move(routes, D, q, Q, max_iterations=10):
#     """Swaps nodes between two different routes if it reduces cost."""
#     for _ in range(max_iterations):
#         improved = False
#         for r1 in range(len(routes)):
#             for r2 in range(len(routes)):
#                 if r1 == r2:
#                     continue

#                 for i in range(1, len(routes[r1]) - 1):
#                     for j in range(1, len(routes[r2]) - 1):
#                         node1, node2 = routes[r1][i], routes[r2][j]

#                         new_route1 = routes[r1][:i] + [node2] + routes[r1][i+1:]
#                         new_route2 = routes[r2][:j] + [node1] + routes[r2][j+1:]

#                         if sum(q[x] for x in new_route1 if x != 0) <= Q and sum(q[x] for x in new_route2 if x != 0) <= Q:
#                             old_cost = sum(D[routes[r1][k]][routes[r1][k+1]] for k in range(len(routes[r1])-1)) + \
#                                        sum(D[routes[r2][k]][routes[r2][k+1]] for k in range(len(routes[r2])-1))

#                             new_cost = sum(D[new_route1[k]][new_route1[k+1]] for k in range(len(new_route1)-1)) + \
#                                        sum(D[new_route2[k]][new_route2[k+1]] for k in range(len(new_route2)-1))

#                             if new_cost < old_cost:
#                                 routes[r1][i], routes[r2][j] = routes[r2][j], routes[r1][i]
#                                 improved = True
#         if not improved:
#             break
#     return routes

# def solve_cvrp(n, Q, D, q):
#     """Solves CVRP with Clarke-Wright + Local Optimization."""
#     routes = clarke_wright_savings(n, Q, D, q)
#     routes = [two_opt(route, D) for route in routes]
#     routes = swap_move(routes, D, q, Q)

#     return routes

# def check(routes, n, Q, q):
#     """Checks validity of solution."""
#     visited = set()
#     capacity_violations = False
#     all_customers = set(range(1, n))

#     for route in routes:
#         total_demand = sum(q[i] for i in route if i != 0)
#         if total_demand > Q:
#             print(f"ERROR: Route {route} exceeds capacity ({total_demand} > {Q})")
#             capacity_violations = True

#         for node in route:
#             if node != 0:
#                 if node in visited:
#                     print(f"ERROR: Customer {node} visited multiple times!")
#                     return False
#                 visited.add(node)

#     missing_customers = all_customers - visited
#     if missing_customers:
#         print(f"ERROR: Missing customers: {missing_customers}")
#         return False

#     return not capacity_violations

# def main():
#     n, Q, D, q = read_input()
#     routes = solve_cvrp(n, Q, D, q)

#     if not routes:
#         print("ERROR: No valid routes found!")
#         return

#     if check(routes, n, Q, q): 
#         for route in routes:
#             print(" ".join(map(str, route)))
#     else:
#         print("ERROR: Invalid solution detected!")

# if __name__ == "__main__":
#     main()
