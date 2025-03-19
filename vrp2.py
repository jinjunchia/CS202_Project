import random
import numpy as np

# Load input data
def load_cvrp_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    n = int(lines[0].strip())  # Number of locations
    Q = int(lines[1].strip())  # Vehicle capacity
    
    # Distance matrix
    D = []
    for i in range(2, 2 + n):
        D.append(list(map(int, lines[i].strip().split())))
    
    # Demand vector
    q = list(map(int, lines[2 + n].strip().split()))
    
    return n, Q, np.array(D), q

# Generate initial population using Nearest Neighbor Heuristic
def nearest_neighbor_solution(n, Q, D, q):
    unvisited = set(range(1, n))
    routes = []
    
    while unvisited:
        route = [0]  # Start from depot
        load = 0
        
        while unvisited:
            last = route[-1]
            next_node = min(unvisited, key=lambda x: D[last][x])
            
            if load + q[next_node] <= Q:
                route.append(next_node)
                load += q[next_node]
                unvisited.remove(next_node)
            else:
                break
        
        route.append(0)  # Return to depot
        routes.append(route)
    
    return routes

# Compute total distance
def total_distance(routes, D):
    return sum(D[route[i]][route[i+1]] for route in routes for i in range(len(route)-1))

# 2-Opt Local Search
def two_opt(route, D):
    best_route = route
    best_distance = sum(D[route[i]][route[i+1]] for i in range(len(route)-1))
    
    for i in range(1, len(route)-2):
        for j in range(i+1, len(route)-1):
            new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
            new_distance = sum(D[new_route[k]][new_route[k+1]] for k in range(len(new_route)-1))
            
            if new_distance < best_distance:
                best_route, best_distance = new_route, new_distance
    
    return best_route

# Genetic Algorithm
def genetic_algorithm(n, Q, D, q, pop_size=50, generations=100, mutation_rate=0.2):
    population = [nearest_neighbor_solution(n, Q, D, q) for _ in range(pop_size)]
    
    for _ in range(generations):
        population.sort(key=lambda x: total_distance(x, D))
        new_population = population[:pop_size//2]  # Select top half
        
        # Crossover
        while len(new_population) < pop_size:
            parent1, parent2 = random.sample(population[:10], 2)
            split = random.randint(1, len(parent1)-2)
            child = parent1[:split] + parent2[split:]
            
            new_population.append(child)
        
        # Mutation (Swap two cities within a route)
        for i in range(len(new_population)):
            if random.random() < mutation_rate:
                route = random.choice(new_population)
                if len(route) > 3:
                    i, j = random.sample(range(1, len(route)-1), 2)
                    route[i], route[j] = route[j], route[i]
        
        # Apply 2-Opt for refinement
        for i in range(len(new_population)):
            for j in range(len(new_population[i])):
                new_population[i][j] = two_opt(new_population[i][j], D)
        
        population = new_population
    
    best_solution = min(population, key=lambda x: total_distance(x, D))
    return best_solution

# Main function
def main():
    filename = "1.in"
    n, Q, D, q = load_cvrp_data(filename)
    best_routes = genetic_algorithm(n, Q, D, q)
    
    for route in best_routes:
        print(" ".join(map(str, route)))

if __name__ == "__main__":
    main()
