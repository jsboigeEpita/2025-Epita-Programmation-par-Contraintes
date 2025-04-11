
from classe import *


def main():
    console = Console()
    console.clear()
    console.print("[bold underline]Minesweeper : Solveur CSP & Jeu Interactif[/bold underline]\n")
    choice = questionary.select(
        "Sélectionnez un mode",
        choices=[
            "Voir les solutions (CSP) pour une grille prédéfinie",
            "Jouer à Minesweeper"
        ]
    ).ask()
    if choice == "Voir les solutions (CSP) pour une grille prédéfinie":
        grid_6x6 = {
            (0, 0): 0, (0, 1): 1, (0, 2): 1, (0, 3): 2, (0, 4): 1, (0, 5): 1,
            (1, 0): 1, (1, 1): "?", (1, 2): "?", (1, 3): "?", (1, 4): "?", (1, 5): 1,
            (2, 0): 1, (2, 1): "?", (2, 2): "?", (2, 3): "?", (2, 4): "?", (2, 5): 2,
            (3, 0): 2, (3, 1): "?", (3, 2): "?", (3, 3): "?", (3, 4): "?", (3, 5): 1,
            (4, 0): 1, (4, 1): "?", (4, 2): "?", (4, 3): "?", (4, 4): "?", (4, 5): 1,
            (5, 0): 1, (5, 1): 1, (5, 2): 2, (5, 3): 1, (5, 4): 1, (5, 5): 0,
        }
        mgrid = MinesweeperGrid(grid_6x6, 6, 6)
        solver = MinesweeperSolver(mgrid)
        solutions = solver.solve()
        console.clear()
        console.print(f"\nNombre de solutions: [bold yellow]{len(solutions)}[/bold yellow]\n")
        for num, solution in enumerate(solutions, start=1):
            console.print(f"Solution {num}:", style="underline bold")
            result_grid = mgrid.apply_solution(solution)
            PrettyPrinter.print_grid(result_grid, mgrid.grid, 6, 6)
            console.print("-" * 40)
        questionary.text("Appuyez sur Entrée pour quitter...").ask()
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
