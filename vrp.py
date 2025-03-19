import sys
import heapq
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

def compute_route_cost(route, D):
    """Computes the total travel distance of a route."""
    return sum(D[route[i]][route[i+1]] for i in range(len(route) - 1))

def two_opt(route, D, max_iterations=100):
    """Improves a given route using the 2-opt algorithm until no further improvement is possible."""
    best_route = route[:]
    best_cost = compute_route_cost(best_route, D)
    
    improved = True
    iteration = 0
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route) - 1):
                # Compute cost difference using incremental update
                old_cost = (
                    D[best_route[i-1]][best_route[i]] + 
                    D[best_route[j]][best_route[j+1]]
                )
                new_cost = (
                    D[best_route[i-1]][best_route[j]] + 
                    D[best_route[i]][best_route[j+1]]
                )

                # If the swap improves the total cost, apply it
                if new_cost < old_cost:
                    best_route[i:j+1] = reversed(best_route[i:j+1])  # Reverse segment
                    best_cost += new_cost - old_cost  # Update cost
                    improved = True

        if not improved:
            break  # Stop when no further improvement is found

    return best_route

def optimize_routes(routes, D):
    """Applies 2-opt optimization to all routes to minimize travel distance."""
    return [two_opt(route, D) for route in routes]

def swap_between_routes(routes, D, q, Q, max_attempts=100):
    """Attempts to swap customers between routes to improve total distance."""
    for _ in range(max_attempts):
        # Pick two different routes
        r1, r2 = random.sample(range(len(routes)), 2)
        route1, route2 = routes[r1], routes[r2]

        if len(route1) < 3 or len(route2) < 3:
            continue  # Skip routes that cannot be modified

        for i in range(1, len(route1) - 1):
            for j in range(1, len(route2) - 1):
                node1, node2 = route1[i], route2[j]

                # Check feasibility after swap
                new_route1 = route1[:i] + [node2] + route1[i+1:]
                new_route2 = route2[:j] + [node1] + route2[j+1:]

                if sum(q[k] for k in new_route1 if k != 0) <= Q and sum(q[k] for k in new_route2 if k != 0) <= Q:
                    # Compute cost change
                    old_cost = compute_route_cost(route1, D) + compute_route_cost(route2, D)
                    new_cost = compute_route_cost(new_route1, D) + compute_route_cost(new_route2, D)

                    if new_cost < old_cost:  # Accept only better swaps
                        routes[r1], routes[r2] = new_route1, new_route2
                        return routes  # Apply the swap and return immediately

    return routes  # Return original if no swaps were found


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
    routes = swap_between_routes(routes, D, q, Q)
    routes = optimize_routes(routes, D)  # Step 3: Apply 2-Opt optimization
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



