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
