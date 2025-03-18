import sys
import math
import random
"""
To use this file with example testcases, run: 

python vrp.py < 1.in > 1.out

This reads input from 1.in and prints output to 1.out. 
"""

#parses the number of locations, capacity, distance matrix and demand

def read_input():
    
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


#n number of locations, Q capacity, q list where q[i] is the demand at the current location, D is a the matrix that represent the distance between location i and j
def knapsack_greedy(n, Q, q, D):
    #assign customers to vehicles using a Greedy Knapsack heuristic
    customers = list(range(1, n))  # exclude depot (0)

    #sort by demand-to-distance ratio to balance routes in descending order with high edmand and close proximity
    customers.sort(key=lambda x: (-q[x] / min(D[x][0], 1)), reverse=True)

    routes = [] #store here and make sure end at depot[0]
    while customers:
        route = [0]  # Start from depot
        remaining_capacity = Q 

        #track customers assigned this round and add each cust to the route and check if they fit and reduce remaining capacity and mark it
        assigned_customers = []
        for customer in customers:
            if q[customer] <= remaining_capacity:
                route.append(customer)
                remaining_capacity -= q[customer]
                assigned_customers.append(customer)

        # prevent empty routes as need to have at least 1 customer
        if len(route) > 1:
            route.append(0)  # return to depot
            routes.append(route)

        # remove assigned customers
        for c in assigned_customers:
            customers.remove(c)

    return routes

#need to check each troute total demand and split the routes that exceed Q with customer still assigned
def rebalance_routes(routes, q, Q):
    #no route exceeds the vehicle capacity by splitting large ones while preserving all customers
    #print("Rebalancing Routes") #debug statement

    new_routes = []
    assigned_customers = set()  # track assigned customers

    #iterate over each route to compute the total demand first without d0
    for route in routes:
        demand = sum(q[i] for i in route if i != 0)

        #split the overloaded routes where it exceeds and make a new route
        if demand > Q:
            #print(f" Route {route} exceeds capacity {Q} (Demand: {demand}). Splitting...")

            current_route = [0]
            remaining_capacity = Q

            #close current route and store the complete in new_route and start new route with remain cap
            for customer in route[1:-1]:  # exclude d0 at start and end
                if q[customer] > remaining_capacity:
                    current_route.append(0)
                    new_routes.append(current_route)
                    current_route = [0]
                    remaining_capacity = Q

                current_route.append(customer)
                assigned_customers.add(customer)
                remaining_capacity -= q[customer]

            # ensure last route is closed properly
            current_route.append(0)
            new_routes.append(current_route)

        else:
            new_routes.append(route)
            assigned_customers.update(set(route[1:-1]))  #  Track assigned customers (excluding depot)

    #previously i did not check so i need to check for missing customer
    all_customers = set(range(1, len(q)))  
    missing_customers = all_customers - assigned_customers

    if missing_customers:
        #print(f"Missing Customers Detected: {missing_customers} - Creating new routes for them.")

        for customer in missing_customers:
            new_routes.append([0, customer, 0])  #  asign each missing customer to their own route

    return new_routes


#https://github.com/ozanyerli/tsp3opt 
#improve the distance by removing three edges and reconnect the route
#ashley tried 2 opt but not as effective where it optimizes each route individually after knapsack
#it removes unnecessary detour and find shorter path to reduce total travel dist
def three_opt(route, D):
    best_distance = route_distance(route, D)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 3):
            for j in range(i + 1, len(route) - 2):
                for k in range(j + 1, len(route) - 1):
                    new_route = route[:i] + route[i:j+1][::-1] + route[j+1:k+1][::-1] + route[k+1:]
                    new_distance = route_distance(new_route, D)
                    if new_distance < best_distance:
                        route = new_route
                        best_distance = new_distance
                        improved = True
    return route
def route_distance(route, D):
    #compute total dist
    return sum(D[route[i]][route[i+1]] for i in range(len(route) - 1))

def optimize_routes(routes, D):
    #call 3-opt
    return [three_opt(route, D) for route in routes]


#3 opt wasnt enough as it is stuck 
#simulated annealing helps to swap rnadom customer between route which accept worse solution with some probability and the cooling down is to converge an optimized solution
def simulated_annealing(routes, D, q, Q, T=1000, cooling_rate=0.995):
    # #print(" Debug: Starting Simulated Annealing...")

    # #copy the current solution and track the best solution found and compute total distance
    # current_routes = routes[:]
    # best_routes = current_routes[:]
    # best_distance = sum(route_distance(r, D) for r in best_routes)

    # #it will run until T is low where the temperature gradually decreases over time, and where higher T allow more random moves while lower T refines it
    # while T > 1:
    #     #print(f"Temp={T:.2f}, Best Distance={best_distance}")

    #     new_routes = current_routes[:]
        
    #     if len(new_routes) < 2:
    #         break  # Avoids IndexError
    #     # select two random routes to swap customers
    #     r1, r2 = random.sample(range(len(new_routes)), 2)

    #     if len(new_routes[r1]) > 3 and len(new_routes[r2]) > 3:
    #         swap_idx1, swap_idx2 = random.randint(1, len(new_routes[r1]) - 2), random.randint(1, len(new_routes[r2]) - 2)

    #         # perform swap
    #         new_routes[r1][swap_idx1], new_routes[r2][swap_idx2] = new_routes[r2][swap_idx2], new_routes[r1][swap_idx1]

    #         #  Check if new routes satisfy capacity
    #         demand_r1 = sum(q[i] for i in new_routes[r1] if i != 0)
    #         demand_r2 = sum(q[i] for i in new_routes[r2] if i != 0)

    #         if demand_r1 > Q or demand_r2 > Q:
    #             #print(f" Invalid swap! Route {new_routes[r1]} (Demand {demand_r1}) or Route {new_routes[r2]} (Demand {demand_r2}) exceeds capacity {Q}")
    #             continue  #  reject swap if violates capacity

    #     new_distance = sum(route_distance(r, D) for r in new_routes)

    #     # accept if better, or with probability if worse
    #     if new_distance < best_distance or random.random() <  math.exp((best_distance - new_distance) / T):
    #         current_routes = new_routes
    #         best_distance = new_distance
    #         best_routes = new_routes

    #     # reduce temperature for next iter
    #     # a little not sure if drop too fast might be stuck in local minimum but if too slow waste time
    #     T *= cooling_rate

    # #print("Simulated Annealing Completed!")
    # return best_routes
    current_routes = routes[:]
    best_routes = current_routes[:]
    best_distance = sum(route_distance(r, D) for r in best_routes)

    while T > 1:
        new_routes = current_routes[:]

        
        if len(new_routes) < 2:
            break  

        r1, r2 = random.sample(range(len(new_routes)), 2)

        if len(new_routes[r1]) > 3 and len(new_routes[r2]) > 3:
            swap_idx1, swap_idx2 = random.randint(1, len(new_routes[r1]) - 2), random.randint(1, len(new_routes[r2]) - 2)
            new_routes[r1][swap_idx1], new_routes[r2][swap_idx2] = new_routes[r2][swap_idx2], new_routes[r1][swap_idx1]

            # Check route validity
            demand_r1 = sum(q[i] for i in new_routes[r1] if i != 0)
            demand_r2 = sum(q[i] for i in new_routes[r2] if i != 0)

            if demand_r1 > Q or demand_r2 > Q:
                continue  

        new_distance = sum(route_distance(r, D) for r in new_routes)

        try:
            accept_probability = math.exp(min(500, (best_distance - new_distance) / max(T, 1)))
        except OverflowError:
            accept_probability = 0

        if new_distance < best_distance or random.random() < accept_probability:
            current_routes = new_routes
            best_distance = new_distance
            best_routes = new_routes

        T *= cooling_rate  # Reduce temperature

    return best_routes



def solve_cvrp(n, Q, D, q):
    #print(" Debug: Solving CVRP...")

    routes = knapsack_greedy(n, Q, q, D)
    #print(f" Initial Routes (Knapsack): {routes}")

    optimized_routes = optimize_routes(routes, D)
    #print(f" After 3-Opt Optimization: {optimized_routes}")

    final_routes = simulated_annealing(optimized_routes, D, q, Q)
    #print(f" Final Routes (Simulated Annealing): {final_routes}")

    # rebalance overload routes
    balanced_routes = rebalance_routes(final_routes, q, Q)
    #print(f" Balanced Routes: {balanced_routes}")

    return balanced_routes

def check(routes, n, Q, D, q):
    node_visited = []
    for route in routes:
        total_demand = sum(q[i] for i in route if i != 0)
        if total_demand > Q:
            return False  #if overload -> false
        
        node_visited += route[1:-1]  #  eclude d0 from checks

    expected_customers = set(range(1, n))  # customers should be exactly {1, 2, ..., n-1}
    visited_customers = set(node_visited)

    if visited_customers != expected_customers:
        #print(f"ERROR: Some customers are missing or duplicated!")
        #print(f"Visited Customers: {sorted(visited_customers)}")
        #print(f"Expected Customers: {sorted(expected_customers)}")
        return False  #  missing or duplicated customers detected

    return True  #solution still witin constraints


def main():
    
    #print(" Debug: start program")

    # read input
    n, Q, D, q = read_input()
    #print(f" input Read: N={n}, Q={Q}")


    routes = solve_cvrp(n, Q, D, q)
    #print(f" routes Generated: {routes}")

    # Check solution validity
    if check(routes, n, Q, D, q): 
        #print("solution is valid")
        for route in routes:
            print(" ".join(map(str, route)))  # Ensures output is printed
    #else:
        #print("solution does not meet constraints!")
    # n, Q, D, q = read_input()
    # routes = solve_cvrp(n, Q, D, q)

    # if check(routes, n, Q, D, q): 
    #     for route in routes:
    #         print(" ".join(map(str, route)))

if __name__ == "__main__":
    main()
