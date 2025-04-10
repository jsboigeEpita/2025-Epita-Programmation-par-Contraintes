from constraint import Problem, ExactSumConstraint

# Exemple de grille : 
# - "?" désigne une case inconnue (variable)
# - Un chiffre (0 à 8) désigne une case ouverte indiquant le nombre de mines autour
# Pour simplifier, on travaille sur une grille 5x5 par exemple.
# On représentera la grille sous forme de dictionnaire : (i, j) -> valeur
# Si la case est inconnue, la valeur est "?".
# Si la case est ouverte, la valeur est le nombre (entier).

# Grille 1 : Exemple de grille 5x5 (celle initiale)
grid1 = {
    (0,0): 1, (0,1): "?", (0,2): "?", (0,3): 1, (0,4): 0,
    (1,0): "?", (1,1): "?", (1,2): "?", (1,3): "?", (1,4): 0,
    (2,0): "?", (2,1): "?", (2,2): 2, (2,3): "?", (2,4): 1,
    (3,0): 1, (3,1): "?", (3,2): "?", (3,3): "?", (3,4): 1,
    (4,0): 0, (4,1): 1, (4,2): 1, (4,3): 1, (4,4): 0,
}

# Grille 2 : Exemple d'une grille 4x4
grid2 = {
    (0,0): "?", (0,1): 1, (0,2): "?", (0,3): 0,
    (1,0): 1, (1,1): "?", (1,2): "?", (1,3): 0,
    (2,0): "?", (2,1): "?", (2,2): 2, (2,3): 1,
    (3,0): 0, (3,1): 1, (3,2): "?", (3,3): 0,
}

# Grille 3 : Exemple d'une grille 3x3
grid3 = {
    (0,0): 0, (0,1): 1, (0,2): "?",
    (1,0): 1, (1,1): "?", (1,2): 1,
    (2,0): "?", (2,1): 1, (2,2): 0,
}

# Liste des grilles avec leur taille respective
grids = [
    (grid1, 5),
    (grid2, 4),
    (grid3, 3)
]

# Fonction pour obtenir les voisins d'une case donnée
def get_neighbors(pos, grid):
    i, j = pos
    neighbors = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue  # ne pas inclure la case elle-même
            neighbor = (i+di, j+dj)
            if neighbor in grid:
                neighbors.append(neighbor)
    return neighbors

# Initialisation du problème CSP
problem = Problem()

# Ajout des variables pour chaque case inconnue
# Chaque variable peut être 0 (pas de mine) ou 1 (mine)
unknown_cells = [pos for pos, val in grid.items() if val == "?"]
for cell in unknown_cells:
    problem.addVariable(cell, [0, 1])

# Pour chaque case ouverte, on ajoute une contrainte d'égalité sur la somme
for pos, val in grid.items():
    if val != "?":
        # Récupérer les voisins inconnus
        neighbors = [n for n in get_neighbors(pos, grid) if grid[n] == "?"]
        if neighbors:  # s'il y a des cases inconnues autour
            # On doit avoir la somme des mines égale à la valeur indiquée
            # Remarque : si certains voisins sont déjà connus (par exemple marqués comme mine dans un traitement antérieur),
            # il faut ajuster la somme attendue.
            problem.addConstraint(ExactSumConstraint(val), neighbors)

# Recherche des solutions
solutions = problem.getSolutions()

# Affichage du nombre de solutions trouvées
print("Nombre de solutions:", len(solutions))

# Optionnel : afficher une solution (si au moins une solution existe)
if solutions:
    solution = solutions[0]
    # Création d'une grille de résultat
    result_grid = {}
    for pos, val in grid.items():
        if val == "?":
            result_grid[pos] = solution[pos]
        else:
            result_grid[pos] = val
    # Affichage simple de la grille
    for i in range(5):
        row = ""
        for j in range(5):
            row += f"{result_grid[(i,j)]} " 
        print(row)
