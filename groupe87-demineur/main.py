from constraint import Problem, ExactSumConstraint

def get_neighbors(pos, grid):
    i, j = pos
    return [(i+di, j+dj) for di in [-1, 0, 1]
                           for dj in [-1, 0, 1]
                           if not (di == 0 and dj == 0) and (i+di, j+dj) in grid]

def add_variables_and_constraints(problem, grid):
    unknown = [pos for pos, val in grid.items() if val == "?"]
    for pos in unknown:
        problem.addVariable(pos, [0, 1])
    for pos, val in grid.items():
        if val != "?":
            neighbors = [n for n in get_neighbors(pos, grid) if grid[n] == "?"]
            if neighbors:
                problem.addConstraint(ExactSumConstraint(val), neighbors)

def solve_grid(grid):
    problem = Problem()
    add_variables_and_constraints(problem, grid)
    return problem.getSolutions()

def apply_solution(grid, solution):
    return {pos: (solution[pos] if val == "?" else val) for pos, val in grid.items()}

def print_grid(grid, size):
    for i in range(size):
        row = " ".join(str(grid[(i, j)]) for j in range(size))
        print(row)

if __name__ == "__main__":
    grid1 = {
        (0,0): 1, (0,1): "?", (0,2): "?", (0,3): 1, (0,4): 0,
        (1,0): "?", (1,1): "?", (1,2): "?", (1,3): "?", (1,4): 0,
        (2,0): "?", (2,1): "?", (2,2): 2, (2,3): "?", (2,4): 1,
        (3,0): 1, (3,1): "?", (3,2): "?", (3,3): "?", (3,4): 1,
        (4,0): 0, (4,1): 1, (4,2): 1, (4,3): 1, (4,4): 0,
    }
    grid2 = {
        (0,0): "?", (0,1): 1, (0,2): "?", (0,3): 0,
        (1,0): 1, (1,1): "?", (1,2): "?", (1,3): 0,
        (2,0): "?", (2,1): "?", (2,2): 2, (2,3): 1,
        (3,0): 0, (3,1): 1, (3,2): "?", (3,3): 0,
    }
    grid3 = {
        (0,0): 0, (0,1): 1, (0,2): "?",
        (1,0): 1, (1,1): "?", (1,2): 1,
        (2,0): "?", (2,1): 1, (2,2): 0,
    }
    grids = [(grid1, 5), (grid2, 4), (grid3, 3)]
    
    for idx, (grid, size) in enumerate(grids, start=1):
        print(f"Grille {idx}")
        solutions = solve_grid(grid)
        print("Nombre de solutions:", len(solutions))
        if solutions:
            res_grid = apply_solution(grid, solutions[0])
            print_grid(res_grid, size)
        print("-" * 20)
        print("Fin de la grille")
