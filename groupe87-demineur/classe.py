import random
import questionary
from constraint import Problem, ExactSumConstraint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# --- Partie CSP et affichage ---

class MinesweeperGrid:
    def __init__(self, grid, rows, cols):
        self.grid = grid
        self.rows = rows
        self.cols = cols

    def get_neighbors(self, pos):
        i, j = pos
        return [
            (i + di, j + dj)
            for di in [-1, 0, 1]
            for dj in [-1, 0, 1]
            if not (di == 0 and dj == 0) and (i + di, j + dj) in self.grid
        ]

    def apply_solution(self, solution):
        return {pos: (solution[pos] if self.grid[pos] == "?" else self.grid[pos])
                for pos in self.grid}

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
    def print_grid(result_grid, original_grid, rows, cols, title="Solution"):
        table = Table(title=title, show_lines=True)
        table.add_column("Row", style="bold magenta", justify="center")
        for j in range(cols):
            table.add_column(f"Col {j}", justify="center")
        for i in range(rows):
            row = [str(i)]
            for j in range(cols):
                pos = (i, j)
                val = result_grid.get(pos, " ")
                orig = original_grid.get(pos, " ")
                if orig == "?":
                    # Dans la solution CSP, on affiche 1 pour mine et 0 pour vide
                    cell_text = "[bold red]1[/bold red]" if val == 1 else "[green]0[/green]"
                else:
                    cell_text = f"[blue]{orig}[/blue]"
                row.append(cell_text)
            table.add_row(*row)
        Console().print(Panel(table, title=title, expand=False))

# --- Partie Jeu interactif ---

class MinesweeperGame:
    def __init__(self, rows, cols, mine_count):
        self.rows = rows
        self.cols = cols
        self.mine_count = mine_count
        self.board = {}
        self.revealed = set()
        self.flagged = set()
        self.game_over = False
        self.win = False
        self.generate_board()

    def generate_board(self):
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        mine_positions = set(random.sample(positions, self.mine_count))
        for pos in positions:
            if pos in mine_positions:
                self.board[pos] = -1  # Mine
            else:
                count = sum(1 for nb in self.get_neighbors(pos) if nb in mine_positions)
                self.board[pos] = count

    def get_neighbors(self, pos):
        r, c = pos
        nbrs = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    nbrs.append((nr, nc))
        return nbrs

    def reveal_cell(self, pos):
        if pos in self.flagged or pos in self.revealed:
            return
        self.revealed.add(pos)
        if self.board[pos] == -1:
            self.game_over = True
        elif self.board[pos] == 0:
            for nb in self.get_neighbors(pos):
                if nb not in self.revealed:
                    self.reveal_cell(nb)

    def toggle_flag(self, pos):
        if pos in self.revealed:
            return
        if pos in self.flagged:
            self.flagged.remove(pos)
        else:
            self.flagged.add(pos)

    def check_win(self):
        total_cells = self.rows * self.cols
        if len(self.revealed) == total_cells - self.mine_count:
            self.win = True
            self.game_over = True

    def print_board(self, reveal_all=False):
        table = Table(show_lines=True)
        table.add_column("Row", style="bold magenta", justify="center")
        for c in range(self.cols):
            table.add_column(f"Col {c}", justify="center")
        for r in range(self.rows):
            row = [str(r)]
            for c in range(self.cols):
                pos = (r, c)
                if reveal_all or pos in self.revealed:
                    if self.board[pos] == -1:
                        cell = "[bold red]M[/bold red]"
                    elif self.board[pos] == 0:
                        cell = "[green] [/green]"
                    else:
                        cell = f"[blue]{self.board[pos]}[/blue]"
                else:
                    cell = "[grey]□[/grey]" if pos not in self.flagged else "[bold yellow]F[/bold yellow]"
                row.append(cell)
            table.add_row(*row)
        Console().print(Panel(table, title="Minesweeper", expand=False))

    def build_csp_grid(self):
        # Construit une grille pour le solveur CSP :
        # les cases révélées affichent leur valeur, les autres sont inconnues ("?")
        grid = {}
        for r in range(self.rows):
            for c in range(self.cols):
                pos = (r, c)
                if pos in self.revealed:
                    grid[pos] = self.board[pos]
                else:
                    grid[pos] = "?"
        return grid

    def solve_with_csp(self):
        csp_grid = self.build_csp_grid()
        mgrid = MinesweeperGrid(csp_grid, self.rows, self.cols)
        solver = MinesweeperSolver(mgrid)
        solutions = solver.solve()
        return mgrid, solutions

    def play(self):
        console = Console()
        while not self.game_over:
            self.print_board()
            action = questionary.select(
                "Choisissez une action",
                choices=[
                    "Ouvrir une case",
                    "Poser/décrocher un drapeau",
                    "Utiliser le solveur (CSP)",
                    "Quitter"
                ]
            ).ask()
            if action == "Quitter":
                console.print("Fin de partie.", style="bold red")
                return
            row = questionary.text("Entrez la ligne :").ask()
            col = questionary.text("Entrez la colonne :").ask()
            try:
                pos = (int(row), int(col))
            except ValueError:
                console.print("Coordonnées invalides.", style="bold red")
                continue
            if not (0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols):
                console.print("Coordonnées hors limites.", style="bold red")
                continue
            if action == "Ouvrir une case":
                self.reveal_cell(pos)
                if self.game_over and self.board[pos] == -1:
                    self.print_board(reveal_all=True)
                    console.print("BOOM ! Vous avez perdu.", style="bold red")
                    return
            elif action == "Poser/décrocher un drapeau":
                self.toggle_flag(pos)
            elif action == "Utiliser le solveur (CSP)":
                mgrid, solutions = self.solve_with_csp()
                if solutions:
                    solution = solutions[0]
                    result_grid = mgrid.apply_solution(solution)
                    PrettyPrinter.print_grid(result_grid, mgrid.grid, self.rows, self.cols, title="Solution CSP")
                else:
                    console.print("Le solveur n'a trouvé aucune solution.", style="bold red")
            self.check_win()
        if self.win:
            self.print_board(reveal_all=True)
            console.print("Félicitations ! Vous avez gagné.", style="bold green")
