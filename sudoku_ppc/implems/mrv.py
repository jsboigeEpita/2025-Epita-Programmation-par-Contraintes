def solve_sudoku_mrv(input_grid):
    """
    Résout un Sudoku en utilisant l'heuristique MRV (Minimum Remaining Values)
    et le forward checking pour propager les contraintes.
    
    Args:
        input_grid: Une grille de Sudoku 9x9 représentée comme une liste de listes.
                   Les cases vides sont représentées par 0.
    
    Returns:
        La grille résolue si une solution existe, None sinon.
    """
    # Crée une copie profonde pour ne pas modifier l'original
    grid = [row.copy() for row in input_grid]
    
    # Domaines pour chaque cellule (valeurs possibles)
    domains = {}
    
    # Initialise les domaines
    for row in range(9):
        for col in range(9):
            pos = (row, col)
            if grid[row][col] == 0:
                domains[pos] = set(range(1, 10))
            else:
                domains[pos] = {grid[row][col]}
    
    # Met à jour les domaines en fonction des contraintes initiales
    for row in range(9):
        for col in range(9):
            if grid[row][col] != 0:
                update_domains(domains, row, col, grid[row][col], grid)
    
    # Essaie de résoudre la grille
    if backtrack_with_mrv(grid, domains):
        return grid
    return None

def update_domains(domains, row, col, value, grid):
    """
    Met à jour les domaines des cellules affectées par un placement.
    """
    # Enlève la valeur des domaines dans la même ligne
    for c in range(9):
        pos = (row, c)
        if grid[row][c] == 0 and pos in domains and value in domains[pos]:
            domains[pos].remove(value)
    
    # Enlève la valeur des domaines dans la même colonne
    for r in range(9):
        pos = (r, col)
        if grid[r][col] == 0 and pos in domains and value in domains[pos]:
            domains[pos].remove(value)
    
    # Enlève la valeur des domaines dans le même bloc 3x3
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            pos = (r, c)
            if grid[r][c] == 0 and pos in domains and value in domains[pos]:
                domains[pos].remove(value)

def backtrack_with_mrv(grid, domains):
    """
    Backtracking avec l'heuristique MRV (Minimum Remaining Values).
    """
    # Vérifie si la grille est complète
    if all(grid[row][col] != 0 for row in range(9) for col in range(9)):
        return True
    
    # Trouve la variable avec le moins de valeurs restantes (MRV)
    min_remaining = 10  # Plus que le maximum possible (9)
    mrv_pos = None
    
    for pos in domains:
        row, col = pos
        if grid[row][col] == 0 and len(domains[pos]) < min_remaining:
            min_remaining = len(domains[pos])
            mrv_pos = pos
            
            # Optimisation: si une cellule n'a qu'une seule valeur possible,
            # il n'est pas nécessaire de chercher plus loin
            if min_remaining == 1:
                break
    
    # Si une variable n'a plus de valeurs possibles, échec
    if min_remaining == 0:
        return False
    
    # Si aucune variable n'a été trouvée, la grille est complète
    if mrv_pos is None:
        return True
    
    row, col = mrv_pos
    
    # Essaie chaque valeur possible
    for value in sorted(domains[mrv_pos]):
        if is_valid(grid, row, col, value):
            # Place la valeur
            grid[row][col] = value
            
            # Sauvegarde les domaines pour pouvoir les restaurer
            old_domains = {pos: set(domains[pos]) for pos in domains}
            
            # Met à jour les domaines
            update_domains(domains, row, col, value, grid)
            
            # Vérifie s'il y a des domaines vides (échec précoce)
            if not any(len(domains[pos]) == 0 for pos in domains if grid[pos[0]][pos[1]] == 0):
                # Récursion
                if backtrack_with_mrv(grid, domains):
                    return True
            
            # Restaure l'état précédent
            grid[row][col] = 0
            for pos in old_domains:
                domains[pos] = old_domains[pos]
    
    return False

def is_valid(grid, row, col, value):
    """
    Vérifie si un placement est valide selon les règles du Sudoku.
    """
    # Vérifie la ligne
    for c in range(9):
        if grid[row][c] == value:
            return False
    
    # Vérifie la colonne
    for r in range(9):
        if grid[r][col] == value:
            return False
    
    # Vérifie le bloc 3x3
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if grid[r][c] == value:
                return False
    
    return True