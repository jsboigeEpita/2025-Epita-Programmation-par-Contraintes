
from classe import *


def main():
    console = Console()
    console.print(
        "[bold underline]Minesweeper : Solveur CSP et Jeu Interactif[/bold underline]")
    console.print("1 : Afficher des solutions avec le solveur (CSP)")
    console.print("2 : Jouer à Minesweeper")
    choice = input("Votre choix (1/2) : ")
    if choice == "1":
        # Exemple avec une grille 5x5 prédéfinie
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
        console.print(
            f"Nombre de solutions: [bold yellow]{len(solutions)}[/bold yellow]")
        for num, solution in enumerate(solutions, start=1):
            console.print(f"\nSolution {num}:", style="underline bold")
            result_grid = mgrid.apply_solution(solution)
            PrettyPrinter.print_grid(result_grid, 5, mgrid.grid)
            console.print("-" * 40)
    elif choice == "2":
        try:
            rows = int(input("Nombre de lignes : "))
            cols = int(input("Nombre de colonnes : "))
            mine_count = int(input("Nombre de mines : "))
        except ValueError:
            console.print("Valeurs invalides.", style="bold red")
            return
        game = MinesweeperGame(rows, cols, mine_count)
        game.play()
    else:
        console.print("Choix invalide.", style="bold red")


if __name__ == "__main__":
    main()
