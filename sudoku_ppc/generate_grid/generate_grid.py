import random

def is_valid(grid, row, col, num):
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

def generate_full_sudoku():
    grid = [[0 for _ in range(9)] for _ in range(9)]
    
    # Remplit les blocs diagonaux 3x3
    for box in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                grid[box + i][box + j] = nums.pop()
    
    # Remplit le reste avec backtracking
    def backtrack(row, col):
        if row == 9:
            return True
        if col == 9:
            return backtrack(row + 1, 0)
        if grid[row][col] != 0:
            return backtrack(row, col + 1)
        
        for num in random.sample(range(1, 10), 9):  # Ordre aléatoire
            if is_valid(grid, row, col, num):
                grid[row][col] = num
                if backtrack(row, col + 1):
                    return True
                grid[row][col] = 0
        return False
    
    backtrack(0, 0)
    return grid

def count_solutions(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                count = 0
                for num in range(1, 10):
                    if is_valid(grid, i, j, num):
                        grid[i][j] = num
                        count += count_solutions(grid)
                        grid[i][j] = 0
                        if count > 1:
                            return count
                return count
    return 1  # Solution unique

def generate_sudoku(difficulty='medium'):
    full_grid = generate_full_sudoku()
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    
    # Nombre de cases à vider selon la difficulté
    to_remove = {
        'facile': 35,
        'moyen': 45,
        'difficile': 55
    }.get(difficulty, 45)
    
    puzzle = [row.copy() for row in full_grid]
    removed = 0
    
    for (i, j) in cells:
        if removed >= to_remove:
            break
        original = puzzle[i][j]
        puzzle[i][j] = 0
        
        # Vérifie que la solution reste unique
        grid_copy = [row.copy() for row in puzzle]
        if count_solutions(grid_copy) == 1:
            removed += 1
        else:
            puzzle[i][j] = original  # Annule la suppression
    
    return puzzle

# Exemple d'utilisation
if __name__ == "__main__":
    sudoku = generate_sudoku('moyen')
    for row in sudoku:
        print(row)