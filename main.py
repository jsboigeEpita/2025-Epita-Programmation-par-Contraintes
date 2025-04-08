from implems.constraint import solve_sudoku_constraint

def print_sudoku(grid):
    """Affiche une grille de Sudoku de manière lisible."""
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 21)
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print("|", end=" ")
            print(grid[i][j] if grid[i][j] != 0 else ".", end=" ")
        print()

def process_sudoku_file(file_path):
    """
    Lit un fichier contenant des grilles de Sudoku et applique solve_sudoku() sur chaque grille.
    
    Format attendu du fichier:
    - Les grilles sont séparées par une ligne vide ou un séparateur clair
    - Chaque grille est représentée sur 9 lignes de 9 chiffres (0 pour les cases vides)
    
    Args:
        file_path (str): Chemin vers le fichier contenant les grilles
        
    Returns:
        list: Liste des grilles résolues (ou None si non résolue)
    """
    solved_grids = []
    
    with open(file_path, 'r') as file:
        current_grid = []
        for line in file:
            line = line.strip()
            if line:
                # Si la ligne contient des chiffres, l'ajouter à la grille courante
                if all(c in '0123456789' for c in line) and len(line) == 9:
                    current_grid.append([int(c) for c in line])
            else:
                # Si ligne vide et grille courante non vide, traiter la grille
                if current_grid:
                    if len(current_grid) == 9:
                        solved_grid = solve_sudoku_constraint(current_grid)
                        solved_grids.append(solved_grid)
                    current_grid = []
        
        # Traiter la dernière grille si le fichier ne se termine pas par une ligne vide
        if current_grid and len(current_grid) == 9:
            solved_grid = solve_sudoku_constraint(current_grid)
            solved_grids.append(solved_grid)
    
    return solved_grids

# Exemple d'utilisation
if __name__ == "__main__":
    # Grille de Sudoku à résoudre (0 = case vide)
    sudoku_grid = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    
    solved_grids = process_sudoku_file("test.txt")
    i = 0;
    for solved_grid in solved_grids:
        if solved_grid:
            print_sudoku(solved_grid)
            print('solved')
        else:
            print("Aucune solution trouvée pour cette grille.")
        i+=1
