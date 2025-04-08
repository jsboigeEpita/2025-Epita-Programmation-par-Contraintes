from constraint import Problem, AllDifferentConstraint



def solve_sudoku_constraint(grid):
    """
    Résout une grille de Sudoku en utilisant la programmation par contraintes.
    
    Args:
        grid: Une grille de Sudoku 9x9 représentée comme une liste de listes.
              Les cases vides sont représentées par 0.
    
    Returns:
        La grille résolue si une solution existe, None sinon.
    """
    # Création du problème de contraintes
    problem = Problem()
    
    # Définition des variables (chaque case de la grille)
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                # Case vide: domaine = 1-9
                problem.addVariable(f'cell_{i}_{j}', range(1, 10))
            else:
                # Case déjà remplie: domaine fixé
                problem.addVariable(f'cell_{i}_{j}', [grid[i][j]])
    
    # Ajout des contraintes
    
    # Contraintes de ligne: toutes les cellules d'une ligne doivent être différentes
    for i in range(9):
        problem.addConstraint(
            AllDifferentConstraint(),
            [f'cell_{i}_{j}' for j in range(9)]
        )
    
    # Contraintes de colonne: toutes les cellules d'une colonne doivent être différentes
    for j in range(9):
        problem.addConstraint(
            AllDifferentConstraint(),
            [f'cell_{i}_{j}' for i in range(9)]
        )
    
    # Contraintes de sous-grille 3x3
    for block_i in range(3):
        for block_j in range(3):
            problem.addConstraint(
                AllDifferentConstraint(),
                [
                    f'cell_{i}_{j}'
                    for i in range(block_i * 3, (block_i + 1) * 3)
                    for j in range(block_j * 3, (block_j + 1) * 3)
                ]
            )
    
    # Résolution du problème
    solution = problem.getSolution()
    
    if solution is None:
        return None
    
    # Reconstruction de la grille résolue
    solved_grid = [[0 for _ in range(9)] for _ in range(9)]
    for i in range(9):
        for j in range(9):
            solved_grid[i][j] = solution[f'cell_{i}_{j}']
    
    return solved_grid

