def solve_sudoku_norvig(grid):
    """
    Résout un Sudoku en utilisant la propagation de contraintes et la recherche
    (inspiré par l'algorithme de Peter Norvig).
    
    Args:
        grid: Une grille de Sudoku 9x9 représentée comme une liste de listes.
              Les cases vides sont représentées par 0.
    
    Returns:
        La grille résolue si une solution existe, None sinon.
    """
    # Convertir la grille en un dictionnaire de positions et valeurs
    values = {}
    digits = '123456789'
    rows = 'ABCDEFGHI'
    cols = digits
    
    # Toutes les cases du Sudoku
    squares = [r+c for r in rows for c in cols]
    
    # Les unités (lignes, colonnes, blocs)
    unit_list = (
        # All rows
        [[r+c for c in cols] for r in rows] +
        # All columns
        [[r+c for r in rows] for c in cols] +
        # All 3x3 boxes
        [[r+c for r in rs for c in cs]
         for rs in ('ABC', 'DEF', 'GHI') 
         for cs in ('123', '456', '789')]
    )
    
    # Dictionnaire associant chaque case à ses unités
    units = {s: [u for u in unit_list if s in u] for s in squares}
    
    # Dictionnaire associant chaque case à ses peers (cases de la même unité)
    peers = {s: set(sum(units[s], [])) - {s} for s in squares}
    
    # Initialisation: assigner les valeurs initiales et les possibilités restantes
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            pos = rows[r] + cols[c]
            values[pos] = digits if val == 0 else str(val)
    
    def assign(values, s, d):
        """Assigne une valeur d à la case s et propage les contraintes."""
        other_values = values[s].replace(d, '')
        if all(eliminate(values, s, d2) for d2 in other_values):
            return values
        return False
    
    def eliminate(values, s, d):
        """Élimine d des valeurs possibles à la case s."""
        if d not in values[s]:
            return values  # Déjà éliminé
        values[s] = values[s].replace(d, '')
        
        # Si une case n'a plus de valeurs possibles, contradiction
        if len(values[s]) == 0:
            return False
        
        # Si une case n'a qu'une valeur possible d2, éliminer d2 des pairs
        if len(values[s]) == 1:
            d2 = values[s]
            if not all(eliminate(values, s2, d2) for s2 in peers[s]):
                return False
        
        # Si une unité n'a qu'une place possible pour d, l'assigner
        for u in units[s]:
            dplaces = [s for s in u if d in values[s]]
            if len(dplaces) == 0:
                return False  # Contradiction: aucune place pour cette valeur
            elif len(dplaces) == 1:
                # d ne peut être placé que dans un seul endroit de cette unité
                if not assign(values, dplaces[0], d):
                    return False
        return values
    
    def search(values):
        """Utilise la recherche avec backtracking pour résoudre le Sudoku."""
        if values is False:
            return False  # Échec précédent
        
        # Vérifie si toutes les cases n'ont qu'une valeur possible
        if all(len(values[s]) == 1 for s in squares):
            return values  # Résolu!
        
        # Choisir la case non résolue avec le moins de possibilités
        n, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
        
        # Essayer chaque valeur possible
        for d in values[s]:
            result = search(assign(values.copy(), s, d))
            if result:
                return result
                
        return False
    
    # Propagation initiale des contraintes
    for s in squares:
        if len(values[s]) == 1:
            d = values[s]
            if not all(eliminate(values, s2, d) for s2 in peers[s]):
                return None  # Contradiction
    
    # Recherche avec backtracking
    values = search(values)
    
    if values:
        # Convertir le résultat en format de grille
        result = [[0 for _ in range(9)] for _ in range(9)]
        for r, row in enumerate(rows):
            for c, col in enumerate(cols):
                result[r][c] = int(values[row+col])
        return result
    else:
        return None