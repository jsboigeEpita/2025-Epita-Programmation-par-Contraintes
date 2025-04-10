from constraint import Problem, ExactSumConstraint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


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
                neighbors = [n for n in self.grid_obj.get_neighbors(
                    pos) if grid[n] == "?"]
                if neighbors:
                    self.problem.addConstraint(
                        ExactSumConstraint(val), neighbors)

    def solve(self):
        self.setup_problem()
        return self.problem.getSolutions()


class PrettyPrinter:
    @staticmethod
    def print_grid(result_grid, size, original_grid):
        table = Table(title="Minesweeper Board", show_lines=True)
        table.add_column("Row", style="bold magenta", justify="center")
        for j in range(size):
            table.add_column(f"Col {j}", justify="center")
        for i in range(size):
            row = [str(i)]
            for j in range(size):
                val = result_grid[(i, j)]
                orig = original_grid[(i, j)]
                if orig == "?":
                    # Soluce d'une case inconnue : 1 = mine, 0 = vide
                    cell_text = "[bold red]1[/bold red]" if val == 1 else "[green]0[/green]"
                else:
                    cell_text = "[blue]" + str(val) + "[/blue]"
                row.append(cell_text)
            table.add_row(*row)
        console = Console()
        console.print(Panel(table, title="Solution", expand=False))


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
        (0, 0): 1, (0, 1): "?", (0, 2): "?", (0, 3): 1, (0, 4): 0, (0, 5): 0,
        (1, 0): "?", (1, 1): "?", (1, 2): "?", (1, 3): "?", (1, 4): 0, (1, 5): 0,
        (2, 0): "?", (2, 1): 2, (2, 2): 2, (2, 3): "?", (2, 4): 1, (2, 5): 0,
        (3, 0): 1, (3, 1): "?", (3, 2): "?", (3, 3): "?", (3, 4): 1, (3, 5): 0,
        (4, 0): 0, (4, 1): 1, (4, 2): 2, (4, 3): 2, (4, 4): 1, (4, 5): 0,
        (5, 0): 0, (5, 1): 0, (5, 2): 1, (5, 3): "?", (5, 4): 1, (5, 5): 0,
    }

    grid7 = {
        (0, 0): 0, (0, 1): 1, (0, 2): "?", (0, 3): "?", (0, 4): "?", (0, 5): 1, (0, 6): 0,
        (1, 0): 1, (1, 1): 2, (1, 2): "?", (1, 3): 3, (1, 4): "?", (1, 5): 2, (1, 6): 1,
        (2, 0): "?", (2, 1): "?", (2, 2): "?", (2, 3): "?", (2, 4): "?", (2, 5): "?", (2, 6): "?",
        (3, 0): 2, (3, 1): "?", (3, 2): "?", (3, 3): 3, (3, 4): "?", (3, 5): "?", (3, 6): 2,
        (4, 0): 1, (4, 1): 2, (4, 2): "?", (4, 3): "?", (4, 4): "?", (4, 5): 2, (4, 6): 1,
        (5, 0): 0, (5, 1): 1, (5, 2): "?", (5, 3): 1, (5, 4): "?", (5, 5): 1, (5, 6): 0,
        (6, 0): 0, (6, 1): 1, (6, 2): 1, (6, 3): 1, (6, 4): 1, (6, 5): 1, (6, 6): 0,
    }

    grid8 = {
        (0, 0): 0, (0, 1): 1, (0, 2): 1, (0, 3): 1, (0, 4): 0,
        (1, 0): 1, (1, 1): "?", (1, 2): "?", (1, 3): "?", (1, 4): 1,
        (2, 0): 1, (2, 1): "?", (2, 2): "?", (2, 3): "?", (2, 4): 1,
        (3, 0): 1, (3, 1): "?", (3, 2): "?", (3, 3): "?", (3, 4): 1,
        (4, 0): 0, (4, 1): 1, (4, 2): 1, (4, 3): 1, (4, 4): 0,
    }
    
    grid9 = {
        (0, 0): 2, (0, 1): "?", (0, 2): "?", (0, 3): 2, (0, 4): "?", (0, 5): 3, (0, 6): 2, (0, 7): "?", (0, 8): "?", (0, 9): 1,
        (1, 0): "?", (1, 1): 3, (1, 2): "?", (1, 3): "?", (1, 4): "?", (1, 5): "?", (1, 6): "?", (1, 7): "?", (1, 8): "?", (1, 9): 1,
        (2, 0): "?", (2, 1): 3, (2, 2): "?", (2, 3): "?", (2, 4): "?", (2, 5): 2, (2, 6): "?", (2, 7): 2, (2, 8): "?", (2, 9): "?",
        (3, 0): "?", (3, 1): "?", (3, 2): "?", (3, 3): 2, (3, 4): 1, (3, 5): "?", (3, 6): "?", (3, 7): "?", (3, 8): 3, (3, 9): "?",
        (4, 0): 3, (4, 1): "?", (4, 2): "?", (4, 3): "?", (4, 4): "?", (4, 5): "?", (4, 6): "?", (4, 7): "?", (4, 8): "?", (4, 9): "?",
        (5, 0): "?", (5, 1): "?", (5, 2): 3, (5, 3): 3, (5, 4): "?", (5, 5): 0, (5, 6): 2, (5, 7): "?", (5, 8): "?", (5, 9): 0,
        (6, 0): "?", (6, 1): "?", (6, 2): "?", (6, 3): "?", (6, 4): "?", (6, 5): "?", (6, 6): "?", (6, 7): "?", (6, 8): 2, (6, 9): "?",
        (7, 0): 1, (7, 1): 2, (7, 2): 5, (7, 3): "?", (7, 4): "?", (7, 5): "?", (7, 6): 2, (7, 7): "?", (7, 8): 5, (7, 9): "?",
        (8, 0): "?", (8, 1): "?", (8, 2): "?", (8, 3): "?", (8, 4): 4, (8, 5): "?", (8, 6): "?", (8, 7): "?", (8, 8): "?", (8, 9): "?",
        (9, 0): "?", (9, 1): 1, (9, 2): "?", (9, 3): 1, (9, 4): 2, (9, 5): "?", (9, 6): "?", (9, 7): 3, (9, 8): 3, (9, 9): 2,

    }
    


    grids = [(grid1, 5), (grid2, 4), (grid3, 3),
             (grid4, 3), (grid5, 3), (grid6, 6), (grid7, 7), (grid8, 5), (grid9, 10)]
    console = Console()
    for idx, (grid, size) in enumerate(grids, start=1):
        console.rule(f"Grille {idx}")
        mgrid = MinesweeperGrid(grid, size)
        solver = MinesweeperSolver(mgrid)
        solutions = solver.solve()
        console.print(
            f"Nombre de solutions: [bold yellow]{len(solutions)}[/bold yellow]")
        for num, solution in enumerate(solutions, start=1):
            console.print(f"\nSolution {num}:", style="underline bold")
            result_grid = mgrid.apply_solution(solution)
            PrettyPrinter.print_grid(result_grid, size, mgrid.grid)
            console.print("-" * 40)
