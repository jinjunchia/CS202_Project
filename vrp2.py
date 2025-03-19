import random

def load_cvrp_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    n = int(lines[0].strip())  # Number of locations
    Q = int(lines[1].strip())  # Vehicle capacity
    
    # Distance matrix
    D = [list(map(int, lines[i].strip().split())) for i in range(2, 2 + n)]
    
    # Demand vector
    q = list(map(int, lines[2 + n].strip().split()))
    
    return n, Q, D, q

def nearest_neighbor_solution(n, Q, D, q):
    unvisited = set(range(1, n))  # Exclude the depot (node 0)
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

def total_distance(routes, D):
    return sum(D[route[i]][route[i+1]] for route in routes for i in range(len(route)-1))

def two_opt(route, D):
    best_route = route[:]
    best_distance = total_distance([route], D)
    improved = True
    max_iter = 100  # Prevent infinite loops
    iteration = 0

    while improved and iteration < max_iter:
        improved = False
        for i in range(1, len(route)-2):
            for j in range(i+1, len(route)-1):
                new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
                new_distance = total_distance([new_route], D)

                if new_distance < best_distance:
                    best_route, best_distance = new_route, new_distance
                    improved = True
        iteration += 1
    
    return best_route

def genetic_algorithm(n, Q, D, q, pop_size=50, generations=100, mutation_rate=0.1):
    population = [nearest_neighbor_solution(n, Q, D, q) for _ in range(pop_size)]

    for _ in range(generations):
        population.sort(key=lambda x: total_distance(x, D))  # Sort by distance (lower is better)
        elite_size = max(1, pop_size // 4)
        new_population = population[:elite_size]
        
        while len(new_population) < pop_size:
            parent1, parent2 = random.sample(population[:elite_size], 2)
            child = []
            for r1, r2 in zip(parent1, parent2):
                if len(r1) > 3:  # Ensure valid crossover range
                    crossover_point = random.randint(1, max(1, len(r1) - 2))
                    child_part = r1[:crossover_point] + [x for x in r2 if x not in r1[:crossover_point]]
                    child.append(child_part)
                else:
                    child.append(r1)  # If too short, keep the parent as-is
            new_population.append(child)

        for i in range(len(new_population)):
            if random.random() < mutation_rate:
                for j in range(len(new_population[i])):
                    route = new_population[i][j]
                    if len(route) > 4:
                        idx1, idx2 = sorted(random.sample(range(1, len(route) - 1), 2))
                        route[idx1], route[idx2] = route[idx2], route[idx1]
        
        for i in range(len(new_population)):
            new_population[i] = [two_opt(route, D) for route in new_population[i]]
        
        population = new_population
    
    best_solution = min(population, key=lambda x: total_distance(x, D))
    return best_solution

def main():
    filename = "3.in"
    n, Q, D, q = load_cvrp_data(filename)
    best_routes = genetic_algorithm(n, Q, D, q)
    
    for route in best_routes:
        print(" ".join(map(str, route)))

if __name__ == "__main__":
    main()
