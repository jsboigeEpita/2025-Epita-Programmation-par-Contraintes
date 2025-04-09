class DancingLinks:
    """
    Implémentation de l'algorithme Dancing Links (DLX) pour résoudre
    des problèmes de couverture exacte.
    """
    def __init__(self):
        self.header = None  # En-tête de la matrice de contraintes
        self.solution = []  # Solution courante
        self.final_solution = None  # Solution finale
        self.found_solution = False  # Indicateur de solution trouvée
    
    class Node:
        """Nœud de la matrice de Dancing Links."""
        def __init__(self, row, col):
            self.row = row  # Identifiant de la ligne
            self.col = col  # Identifiant de la colonne
            
            # Pointeurs pour les liens circulaires
            self.left = self
            self.right = self
            self.up = self
            self.down = self
            
            # Colonne du nœud (pour les nœuds de données)
            # Taille de la colonne (pour les nœuds d'en-tête)
            self.column = None
            self.size = 0
    
    def create_header(self, num_cols):
        """Crée l'en-tête de la matrice avec le nombre spécifié de colonnes."""
        self.header = self.Node(-1, -1)  # Nœud d'en-tête principal
        prev_node = self.header
        
        # Crée les nœuds d'en-tête pour chaque colonne
        for col in range(num_cols):
            new_node = self.Node(-1, col)
            new_node.column = new_node  # Le nœud d'en-tête de colonne pointe vers lui-même
            
            # Insère le nouveau nœud dans la liste circulaire horizontale
            new_node.left = prev_node
            prev_node.right = new_node
            new_node.right = self.header
            self.header.left = new_node
            
            prev_node = new_node
    
    def add_row(self, row, cols):
        """
        Ajoute une ligne à la matrice.
        row: identifiant de la ligne
        cols: liste des indices de colonnes où cette ligne a des 1
        """
        prev_node = None
        first_node = None
        
        for col in cols:
            # Crée un nouveau nœud
            new_node = self.Node(row, col)
            
            # Trouve le nœud d'en-tête de colonne
            col_node = self.header
            for _ in range(col + 1):
                col_node = col_node.right
            
            # Insère le nouveau nœud dans la liste circulaire verticale
            new_node.up = col_node.up
            col_node.up.down = new_node
            new_node.down = col_node
            col_node.up = new_node
            
            # Associe le nœud à sa colonne
            new_node.column = col_node
            
            # Incrémente la taille de la colonne
            col_node.size += 1
            
            # Insère le nouveau nœud dans la liste circulaire horizontale
            if prev_node:
                new_node.left = prev_node
                prev_node.right = new_node
            else:
                first_node = new_node
            
            prev_node = new_node
        
        # Complète la liste circulaire horizontale
        if first_node and prev_node:
            first_node.left = prev_node
            prev_node.right = first_node
    
    def cover_column(self, col_node):
        """Couvre une colonne en la retirant de la matrice."""
        col_node.right.left = col_node.left
        col_node.left.right = col_node.right
        
        i = col_node.down
        while i != col_node:
            j = i.right
            while j != i:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1
                j = j.right
            i = i.down
    
    def uncover_column(self, col_node):
        """Découvre une colonne précédemment couverte."""
        i = col_node.up
        while i != col_node:
            j = i.left
            while j != i:
                j.column.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up
        
        col_node.right.left = col_node
        col_node.left.right = col_node
    
    def search(self, k):
        """
        Recherche récursive de solutions (Algorithme X de Knuth).
        k: profondeur de recherche actuelle
        """
        if self.found_solution:
            return
        
        # Si l'en-tête est vide, une solution a été trouvée
        if self.header.right == self.header:
            self.final_solution = self.solution.copy()
            self.found_solution = True
            return
        
        # Choix de la colonne avec le moins de nœuds (heuristique de Knuth)
        min_size = float('inf')
        col_node = None
        j = self.header.right
        
        while j != self.header:
            if j.size < min_size:
                min_size = j.size
                col_node = j
            j = j.right
        
        # Couvre la colonne choisie
        self.cover_column(col_node)
        
        # Explore toutes les lignes de cette colonne
        r = col_node.down
        while r != col_node:
            self.solution.append(r.row)
            
            # Couvre toutes les colonnes touchées par cette ligne
            j = r.right
            while j != r:
                self.cover_column(j.column)
                j = j.right
            
            # Appel récursif
            self.search(k + 1)
            
            if self.found_solution:
                return
            
            # Retour en arrière
            self.solution.pop()
            
            # Découvre toutes les colonnes touchées par cette ligne
            j = r.left
            while j != r:
                self.uncover_column(j.column)
                j = j.left
            
            r = r.down
        
        # Découvre la colonne choisie
        self.uncover_column(col_node)


def solve_sudoku_dlx(grid):
    """
    Résout un Sudoku en utilisant l'algorithme Dancing Links (DLX).
    
    Args:
        grid: Une grille de Sudoku 9x9 représentée comme une liste de listes.
              Les cases vides sont représentées par 0.
    
    Returns:
        La grille résolue si une solution existe, None sinon.
    """
    # Crée une instance de DancingLinks
    dlx = DancingLinks()
    
    # Le problème du Sudoku a 4 contraintes:
    # 1. Chaque case doit avoir un chiffre
    # 2. Chaque ligne doit contenir les chiffres 1-9
    # 3. Chaque colonne doit contenir les chiffres 1-9
    # 4. Chaque bloc 3x3 doit contenir les chiffres 1-9
    
    # Nombre total de contraintes: 9x9 + 9x9 + 9x9 + 9x9 = 324
    num_constraints = 4 * 9 * 9
    
    # Crée l'en-tête de la matrice
    dlx.create_header(num_constraints)
    
    # Carte les indices de contraintes
    def get_constraint_index(constraint_type, i, j, val):
        if constraint_type == 0:  # Case (i,j) a une valeur
            return i * 9 + j
        elif constraint_type == 1:  # Ligne i a la valeur val
            return 81 + i * 9 + (val - 1)
        elif constraint_type == 2:  # Colonne j a la valeur val
            return 162 + j * 9 + (val - 1)
        else:  # Bloc (i//3, j//3) a la valeur val
            block = (i // 3) * 3 + (j // 3)
            return 243 + block * 9 + (val - 1)
    
    # Pour chaque case possible, ajoute une ligne à la matrice
    row_id = 0
    for i in range(9):
        for j in range(9):
            # Si la case a déjà une valeur, n'ajoute qu'une ligne pour cette valeur
            if grid[i][j] != 0:
                val = grid[i][j]
                # Cette ligne satisfait les 4 contraintes pour la valeur donnée
                constraints = [
                    get_constraint_index(0, i, j, val),  # Case (i,j) a une valeur
                    get_constraint_index(1, i, j, val),  # Ligne i a la valeur val
                    get_constraint_index(2, i, j, val),  # Colonne j a la valeur val
                    get_constraint_index(3, i, j, val)   # Bloc a la valeur val
                ]
                dlx.add_row(row_id, constraints)
                row_id += 1
            else:
                # Pour les cases vides, considère toutes les valeurs possibles
                for val in range(1, 10):
                    # Chaque valeur possible satisfait les 4 contraintes
                    constraints = [
                        get_constraint_index(0, i, j, val),
                        get_constraint_index(1, i, j, val),
                        get_constraint_index(2, i, j, val),
                        get_constraint_index(3, i, j, val)
                    ]
                    dlx.add_row(row_id, constraints)
                    row_id += 1
    
    # Commence la recherche
    dlx.search(0)
    
    if dlx.final_solution:
        # Convertit la solution de DLX en grille de Sudoku
        result = [row.copy() for row in grid]  # Copie la grille d'entrée
        
        # Pour chaque ligne de la solution
        for row_index in dlx.final_solution:
            # Décode la ligne pour obtenir la case et la valeur
            # Pour les cases préremplies, row_index < 81
            if row_index < 81:
                continue  # Déjà dans la grille d'entrée
            
            # Pour les cases vides, row_index est entre 81 et 81 + 9*9*9 - 1
            row_index -= 81  # Ajusté pour les cases préremplies
            
            # Calcule i, j, val à partir de row_index
            i = row_index // (9 * 9)
            remainder = row_index % (9 * 9)
            j = remainder // 9
            val = remainder % 9 + 1
            
            result[i][j] = val
        
        return result
    else:
        return None

def solve_sudoku_dlx_simple(grid):
    """
    Version simplifiée utilisant Dancing Links pour résoudre un Sudoku.
    Cette version est une interface plus simple pour solve_sudoku_dlx.
    
    Args:
        grid: Une grille de Sudoku 9x9 représentée comme une liste de listes.
              Les cases vides sont représentées par 0.
    
    Returns:
        La grille résolue si une solution existe, None sinon.
    """
    # Crée un tableau pour stocker les indices des cases préremplies
    filled_cells = []
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                filled_cells.append((i, j, grid[i][j]))
    
    # Crée une grille vide
    empty_grid = [[0 for _ in range(9)] for _ in range(9)]
    
    # Essaie de résoudre le Sudoku vide
    result = solve_sudoku_dlx(empty_grid)
    
    if result:
        # Vérifie si la solution est compatible avec les cases préremplies
        for i, j, val in filled_cells:
            if result[i][j] != val:
                return None  # Incompatible
        return result
    else:
        return None