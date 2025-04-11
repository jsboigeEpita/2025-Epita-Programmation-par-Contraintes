

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
    Lit un fichier contenant des grilles de Sudoku et retourne la liste des grilles
    
    Format attendu du fichier:
    - Les grilles sont séparées par une ligne vide ou un séparateur clair
    - Chaque grille est représentée sur 9 lignes de 9 chiffres (0 pour les cases vides)
    
    Args:
        file_path (str): Chemin vers le fichier contenant les grilles
        
    Returns:
        list: Liste des grilles
    """
    grids = []
    
    with open(file_path, 'r') as file:
        current_grid = []
        for line in file:
            line = line.strip()
            if line:
                # Si la ligne contient des chiffres, l'ajouter à la grille courante
                if all(c in '0123456789' for c in line) and len(line) == 9:
                    current_grid.append([int(c) for c in line])
            else:
                # Si ligne vide et grille courante non vide, ajouter la grille à la liste
                if current_grid:
                    grids.append(current_grid)
                current_grid = []
        
        # Traiter la dernière grille si le fichier ne se termine pas par une ligne vide
        if current_grid and len(current_grid) == 9:
            grids.append(current_grid)
    
    return grids