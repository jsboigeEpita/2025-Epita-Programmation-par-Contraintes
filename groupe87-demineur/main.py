from constraint import Problem, ExactSumConstraint

class MinesweeperGrid:
    def __init__(self, grid, size):
        self.grid = grid
        self.size = size

    def get_neighbors(self, pos):
        i, j = pos
        return [
            (i + di, j + dj)
            for di in [-1, 0, 1]
            for dj in [-1, 0, 1]
            if not (di == 0 and dj == 0) and (i + di, j + dj) in self.grid
        ]

    def apply_solution(self, solution):
        return {pos: (solution[pos] if val == "?" else val)
                for pos, val in self.grid.items()}

class MinesweeperSolver:
    def __init__(self, minesweeper_grid):
        self.grid_obj = minesweeper_grid
        self.problem = Problem()

    def setup_problem(self):
        grid = self.grid_obj.grid
        unknown = [pos for pos, val in grid.items() if val == "?"]
        for pos in unknown:
            self.problem.addVariable(pos, [0, 1])
        for pos, val in grid.items():
            if val != "?":
                neighbors = [n for n in self.grid_obj.get_neighbors(pos) if grid[n] == "?"]
                if neighbors:
                    self.problem.addConstraint(ExactSumConstraint(val), neighbors)

    def solve(self):
        self.setup_problem()
        return self.problem.getSolutions()

class PrettyPrinter:
    @staticmethod
    def print_grid(grid, size):
        border = "+---" * size + "+"
        print(border)
        for i in range(size):
            row = ""
            for j in range(size):
                row += f"| {grid[(i, j)]} "
            print(row + "|")
            print(border)

if __name__ == "__main__":
    grid1 = {
        (0, 0): 1, (0, 1): "?", (0, 2): "?", (0, 3): 1, (0, 4): 0,
        (1, 0): "?", (1, 1): "?", (1, 2): "?", (1, 3): "?", (1, 4): 0,
        (2, 0): "?", (2, 1): "?", (2, 2): 2, (2, 3): "?", (2, 4): 1,
        (3, 0): 1, (3, 1): "?", (3, 2): "?", (3, 3): "?", (3, 4): 1,
        (4, 0): 0, (4, 1): 1, (4, 2): 1, (4, 3): 1, (4, 4): 0,
    }
    grid2 = {
        (0, 0): "?", (0, 1): 1, (0, 2): "?", (0, 3): 0,
        (1, 0): 1, (1, 1): "?", (1, 2): "?", (1, 3): 0,
        (2, 0): "?", (2, 1): "?", (2, 2): 2, (2, 3): 1,
        (3, 0): 0, (3, 1): 1, (3, 2): "?", (3, 3): 0,
    }
    grid3 = {
        (0, 0): 0, (0, 1): 1, (0, 2): "?",
        (1, 0): 1, (1, 1): "?", (1, 2): 1,
        (2, 0): "?", (2, 1): 1, (2, 2): 0,
    }
    grid4 = {
        (0, 0): 1, (0, 1): "?", (0, 2): "?",
        (1, 0): "?", (1, 1): "?", (1, 2): 0,
        (2, 0): "?", (2, 1): 1, (2, 2): 0,
    }
    grid5 = {
        (0, 0): 1, (0, 1): "?", (0, 2): "?",
        (1, 0): "?", (1, 1): "?", (1, 2): "?",
        (2, 0): 0, (2, 1): "?", (2, 2): 0,
    }
    
    grid6 = {
    (0,0): 1, (0,1): "?", (0,2): "?", (0,3): 1, (0,4): 0, (0,5): 0,
    (1,0): "?", (1,1): "?", (1,2): "?", (1,3): "?", (1,4): 0, (1,5): 0,
    (2,0): "?", (2,1): 2, (2,2): 2, (2,3): "?", (2,4): 1, (2,5): 0,
    (3,0): 1, (3,1): "?", (3,2): "?", (3,3): "?", (3,4): 1, (3,5): 0,
    (4,0): 0, (4,1): 1, (4,2): 2, (4,3): 2, (4,4): 1, (4,5): 0,
    (5,0): 0, (5,1): 0, (5,2): 1, (5,3): "?", (5,4): 1, (5,5): 0,
}
    
    grids = [(grid1, 5), (grid2, 4), (grid3, 3), (grid4, 3), (grid5, 3)]

    for idx, (grid, size) in enumerate(grids, start=1):
        print(f"Grille {idx}")
        mgrid = MinesweeperGrid(grid, size)
        solver = MinesweeperSolver(mgrid)
        solutions = solver.solve()
        print("Nombre de solutions:", len(solutions))
        for num, solution in enumerate(solutions, start=1):
            print(f"Solution {num}:")
            result_grid = mgrid.apply_solution(solution)
            PrettyPrinter.print_grid(result_grid, size)
            print("-" * 20)
