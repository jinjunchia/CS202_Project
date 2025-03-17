import itertools
import numpy as np

# Read input from file
with open("1.in", "r") as file:
    lines = file.readlines()

# Extract number of locations (N) and vehicle capacity (Q)
N = int(lines[0].strip())  # First line contains N (Number of locations)
Q = int(lines[1].strip())  # Second line contains Q (Vehicle capacity)

# Extract distance matrix
distance_matrix = []
for i in range(2, 2 + N):  # Next N lines contain the distance matrix
    distance_matrix.append(list(map(int, lines[i].split())))

# Extract demand list (last line)
demand = list(map(int, lines[2 + N].split()))
# Define the DP Table
dp = np.full((N, Q + 1), float('inf'))  # DP[i][q] = min cost to serve first i customers with q capacity left
dp[0][:] = 0  # Starting at depot, cost is 0

# Fill the DP Table (Knapsack-like logic)
for i in range(1, N):  # Iterate over customers
    for q in range(Q + 1):  # Iterate over all capacities
        dp[i][q] = dp[i - 1][q]  # Exclude customer
        if demand[i] <= q:
            dp[i][q] = min(dp[i][q], dp[0][q - demand[i]] + distance_matrix[0][i])

# Find the optimal assignment of customers to vehicles
def construct_routes_with_dp():
    unvisited = set(range(1, N))  # Customers (1 to N-1)
    routes = []

    while unvisited:
        route = [0]  # Start at depot
        capacity_left = Q

        # Use DP to determine which subset of customers minimizes cost
        while unvisited:
            # Choose the next customer that results in the lowest DP[i][q] cost
            next_customer = min(
                unvisited,
                key=lambda c: dp[c][capacity_left] if (demand[c] <= capacity_left and distance_matrix[0][c] != 999) else float('inf'),
                default=None
            )

            # If no customer fits in the remaining capacity, return to depot
            if next_customer is None or demand[next_customer] > capacity_left or distance_matrix[0][next_customer] == 999:
                break

            route.append(next_customer)
            capacity_left -= demand[next_customer]
            unvisited.remove(next_customer)

        route.append(0)  # End at depot
        routes.append(route)

    return routes

def two_opt(route, distance_matrix):
    """Applies the 2-opt optimization to improve the given route."""
    best_route = route
    best_distance = calculate_route_distance(route, distance_matrix)
    
    for i in range(1, len(route) - 2):  # Avoid depot at index 0
        for j in range(i + 1, len(route) - 1):  # Ensure valid swap range
            new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
            new_distance = calculate_route_distance(new_route, distance_matrix)
            
            if new_distance < best_distance:
                best_route = new_route
                best_distance = new_distance
                
    return best_route

def swap_between_routes(routes, distance_matrix, demand, Q):
    """
    Try moving customers between routes to minimize total distance.
    Returns improved routes.
    """
    best_routes = routes.copy()
    best_total_cost = sum(calculate_route_distance(r, distance_matrix) for r in routes)

    for i in range(len(routes)):
        for j in range(i + 1, len(routes)):  # Compare two different routes
            route1, route2 = routes[i], routes[j]

            for k in range(1, len(route1) - 1):  # Avoid swapping depot
                for m in range(1, len(route2) - 1):
                    new_route1 = route1[:k] + [route2[m]] + route1[k+1:]
                    new_route2 = route2[:m] + [route1[k]] + route2[m+1:]

                    # Check if capacity constraints are met
                    if sum(demand[c] for c in new_route1 if c != 0) > Q:
                        continue
                    if sum(demand[c] for c in new_route2 if c != 0) > Q:
                        continue

                    # Compute new total cost
                    new_cost = calculate_route_distance(new_route1, distance_matrix) + \
                               calculate_route_distance(new_route2, distance_matrix)

                    # If new configuration is better, update
                    if new_cost < best_total_cost and abs(sum(demand[c] for c in new_route1 if c != 0) - sum(demand[c] for c in new_route2 if c != 0)) <= 3:
                        best_routes[i] = new_route1
                        best_routes[j] = new_route2
                        best_total_cost = new_cost

    return best_routes

def calculate_route_distance(route, distance_matrix):
    """Calculates the total travel cost of a given route."""
    return sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route) - 1))

# Print the Optimized Routes
optimized_routes = [two_opt(route, distance_matrix) for route in construct_routes_with_dp()]

final_routes = swap_between_routes(optimized_routes, distance_matrix, demand, Q)

# Print final improved routes
for route in final_routes:
    print("Final Optimized Route:", " → ".join(map(str, route)))


