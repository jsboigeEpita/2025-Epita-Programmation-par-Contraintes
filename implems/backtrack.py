def find_empty_cell(grid):
    """Trouve la prochaine cellule vide (valeur 0) dans la grille"""
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                return (row, col)
    return None

def is_valid(grid, row, col, num):
    """Vérifie si un nombre peut être placé dans une cellule (identique à votre version existante)"""
    # Vérifie la ligne
    if num in grid[row]:
        return False
    
    # Vérifie la colonne
    for i in range(9):
        if grid[i][col] == num:
            return False
    
    # Vérifie le bloc 3x3
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if grid[start_row + i][start_col + j] == num:
                return False
    return True

def solve_sudoku_backtracking(input_grid):
    """Résout un Sudoku et retourne la grille solution complète"""
    # Crée une copie profonde pour ne pas modifier l'original
    grid = [row.copy() for row in input_grid]
    
    def backtrack():
        cell = find_empty_cell(grid)
        if not cell:
            return True  # Sudoku résolu
        
        row, col = cell
        for num in range(1, 10):
            if is_valid(grid, row, col, num):
                grid[row][col] = num
                if backtrack():
                    return True
                grid[row][col] = 0  # Backtrack
        return False
    
    # Retourne la grille résolue ou None si pas de solution
    return grid if backtrack() else None