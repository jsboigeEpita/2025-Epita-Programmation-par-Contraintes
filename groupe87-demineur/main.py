
from classe import *

def main():
    console = Console()
    console.print("[bold underline]Minesweeper : Solveur CSP & Jeu Interactif[/bold underline]\n")
    choice = questionary.select(
        "Sélectionnez un mode",
        choices=[
            "Voir les solutions (CSP)",
            "Jouer à Minesweeper"
        ]
    ).ask()
    if choice == "Voir les solutions (CSP)":
        grid5x5 = {
            (0, 0): 0, (0, 1): 1, (0, 2): 1, (0, 3): 1, (0, 4): 0,
            (1, 0): 1, (1, 1): "?", (1, 2): "?", (1, 3): "?", (1, 4): 1,
            (2, 0): 1, (2, 1): "?", (2, 2): "?", (2, 3): "?", (2, 4): 1,
            (3, 0): 1, (3, 1): "?", (3, 2): "?", (3, 3): "?", (3, 4): 1,
            (4, 0): 0, (4, 1): 1, (4, 2): 1, (4, 3): 1, (4, 4): 0,
        }
        mgrid = MinesweeperGrid(grid5x5, 5)
        solver = MinesweeperSolver(mgrid)
        solutions = solver.solve()
        console.print(f"\nNombre de solutions: [bold yellow]{len(solutions)}[/bold yellow]\n")
        for num, solution in enumerate(solutions, start=1):
            console.print(f"Solution {num}:", style="underline bold")
            result_grid = mgrid.apply_solution(solution)
            PrettyPrinter.print_grid(result_grid, 5, mgrid.grid)
            console.print("-" * 40)
    elif choice == "Jouer à Minesweeper":
        rows = int(questionary.text("Nombre de lignes :", default="9").ask())
        cols = int(questionary.text("Nombre de colonnes :", default="9").ask())
        mine_count = int(questionary.text("Nombre de mines :", default="10").ask())
        game = MinesweeperGame(rows, cols, mine_count)
        game.play()
    else:
        console.print("Choix invalide.", style="bold red")

if __name__ == "__main__":
    main()
