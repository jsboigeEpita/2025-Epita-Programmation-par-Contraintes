import time
import numpy as np
from typing import Tuple, List, Set, Dict, Optional
from minesweeper import Minesweeper
import constraint

class MinesweeperCSPSolver:
    """
    Solveur de Démineur utilisant la programmation par contraintes avec python-constraint.
    """
    
    def __init__(self, game: Minesweeper):
        """
        Initialise le solveur avec une instance de jeu.
        
        Args:
            game: Instance du jeu Démineur à résoudre
        """
        self.game = game
        self.width = game.width
        self.height = game.height
        self.board = game.get_visible_board()
        self.num_mines = game.num_mines
        
        # Positions des cellules non révélées
        self.unknown_cells = []
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col] == Minesweeper.UNKNOWN or self.board[row, col] == Minesweeper.FLAG:
                    self.unknown_cells.append((row, col))
        
        # Résultats de l'analyse
        self.safe_cells: Set[Tuple[int, int]] = set()
        self.mine_cells: Set[Tuple[int, int]] = set()
        
    def solve(self, use_probability: bool = False) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Résout le problème du Démineur en utilisant la propagation de contraintes.
        
        Args:
            use_probability: Si True, utilise des probabilités pour les cas ambigus
            
        Returns:
            Tuple contenant deux ensembles: les cellules sûres et les cellules avec mines
        """
        start_time = time.time()
        
        # Réinitialiser les résultats
        self.safe_cells = set()
        self.mine_cells = set()
        
        # Si aucune cellule inconnue, retourner les ensembles vides
        if not self.unknown_cells:
            return self.safe_cells, self.mine_cells
        
        # Créer le problème CSP
        problem = constraint.Problem()
        
        # Variables: une par cellule non révélée (0 = pas de mine, 1 = mine)
        for row, col in self.unknown_cells:
            problem.addVariable(f"cell_{row}_{col}", [0, 1])
        
        # Contrainte: le nombre total de mines
        problem.addConstraint(
            constraint.ExactSumConstraint(self.num_mines),
            [f"cell_{row}_{col}" for row, col in self.unknown_cells]
        )
        
        # Contraintes pour chaque cellule révélée avec un chiffre
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col] >= 0:  # Cellule avec un nombre
                    adjacent_cells = self.game.get_unknown_adjacent_cells(row, col)
                    if adjacent_cells:  # S'il y a des cellules adjacentes inconnues
                        # Calculer le nombre de mines restantes à trouver
                        value = self.board[row, col]
                        flagged_adjacent = [(r, c) for r, c in adjacent_cells 
                                          if self.board[r, c] == Minesweeper.FLAG]
                        remaining_mines = value - len(flagged_adjacent)
                        
                        # Variables pour les cellules adjacentes non marquées
                        adjacent_vars = [f"cell_{r}_{c}" for r, c in adjacent_cells 
                                      if self.board[r, c] != Minesweeper.FLAG]
                        
                        if adjacent_vars:
                            problem.addConstraint(
                                constraint.ExactSumConstraint(remaining_mines),
                                adjacent_vars
                            )
        
        # Obtenir toutes les solutions possibles
        solutions = problem.getSolutions()
        
        if not solutions:
            print("Le problème n'a pas de solution.")
            return self.safe_cells, self.mine_cells
        
        # Compter la fréquence de chaque cellule contenant une mine
        mine_counts = {}
        for cell in self.unknown_cells:
            row, col = cell
            var_name = f"cell_{row}_{col}"
            mine_counts[cell] = sum(sol[var_name] for sol in solutions)
        
        # Normaliser les fréquences
        num_solutions = len(solutions)
        probabilities = {cell: count / num_solutions for cell, count in mine_counts.items()}
        
        # Identifier les cellules sûres et les mines certaines
        for cell, prob in probabilities.items():
            if prob == 0:  # Jamais une mine dans aucune solution
                self.safe_cells.add(cell)
            elif prob == 1:  # Toujours une mine dans toutes les solutions
                self.mine_cells.add(cell)
        
        # Si demandé et qu'aucune cellule sûre/mine n'a été trouvée, utiliser l'approche probabiliste
        if use_probability and not self.safe_cells and not self.mine_cells and probabilities:
            # Trouver la cellule la plus sûre
            safest_cell = min(probabilities.items(), key=lambda x: x[1])
            if safest_cell[1] < 0.3:  # Si probabilité < 30%, considérer comme sûre
                self.safe_cells.add(safest_cell[0])
                
            # Trouver les cellules qui sont très probablement des mines
            for cell, prob in probabilities.items():
                if prob > 0.9:  # Si probabilité > 90%, considérer comme mine
                    self.mine_cells.add(cell)
            
        elapsed_time = time.time() - start_time
        print(f"Résolution terminée en {elapsed_time:.2f} secondes.")
        print(f"Cellules sûres trouvées: {len(self.safe_cells)}")
        print(f"Mines identifiées: {len(self.mine_cells)}")
        
        return self.safe_cells, self.mine_cells
    
    def update_game(self, auto_play: bool = False) -> bool:
        """
        Met à jour le jeu avec les résultats de l'analyse.
        
        Args:
            auto_play: Si True, joue automatiquement les cellules sûres
            
        Returns:
            True si le jeu a été mis à jour, False sinon
        """
        updated = False
        board = self.game.get_visible_board()  # Get current board state
        
        # Marquer les mines avec des drapeaux
        for row, col in self.mine_cells:
            if board[row, col] == Minesweeper.UNKNOWN:
                self.game.toggle_flag(row, col)
                updated = True
        
        # Révéler les cellules sûres
        if auto_play:
            for row, col in self.safe_cells:
                if board[row, col] == Minesweeper.UNKNOWN:
                    self.game.reveal(row, col)
                    updated = True
                    
        return updated
    
    def get_safe_cells(self) -> Set[Tuple[int, int]]:
        """
        Retourne l'ensemble des cellules identifiées comme sûres.
        
        Returns:
            Ensemble des positions (row, col) des cellules sûres
        """
        return self.safe_cells
    
    def get_mine_cells(self) -> Set[Tuple[int, int]]:
        """
        Retourne l'ensemble des cellules identifiées comme contenant des mines.
        
        Returns:
            Ensemble des positions (row, col) des cellules avec mines
        """
        return self.mine_cells
        
    def solve_step(self, game=None) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Alias pour la méthode solve(), maintient la compatibilité avec l'interface
        attendue dans simple_csp_cli.py.
        
        Args:
            game: Instance du jeu Démineur (ignoré, utilisé pour compatibilité)
            
        Returns:
            Tuple contenant deux ensembles: les cellules sûres et les cellules avec mines
        """
        # Mettre à jour l'état du jeu si un nouveau jeu est fourni
        if game is not None and game != self.game:
            self.game = game
            self.width = game.width
            self.height = game.height
            self.board = game.get_visible_board()
            
            # Mettre à jour les cellules inconnues
            self.unknown_cells = []
            for row in range(self.height):
                for col in range(self.width):
                    if self.board[row, col] == Minesweeper.UNKNOWN or self.board[row, col] == Minesweeper.FLAG:
                        self.unknown_cells.append((row, col))
        
        # Utiliser la méthode solve existante
        return self.solve()

    def step_by_step_solve(self, update_callback=None):
        """
        Résout le jeu pas à pas, en appelant le callback après chaque étape.
        
        Args:
            update_callback: Fonction de callback appelée après chaque mise à jour
            
        Yields:
            Le jeu après chaque étape de résolution
        """
        while not self.game.game_over:
            # Faire une étape de résolution
            self.solve()
            
            # Mettre à jour le jeu
            updated = self.update_game(auto_play=True)
            
            # Si aucune mise à jour n'a été faite, on ne peut plus progresser
            if not updated:
                break
                
            # Appeler le callback si fourni
            if update_callback:
                update_callback(self.game)
                
            # Yielder le jeu mis à jour
            yield self.game


class SimpleMinesweeperSolver:
    """
    Solveur de Démineur utilisant des règles simples de déduction.
    Cette implémentation est plus rapide mais moins puissante que l'approche CSP.
    """
    
    def __init__(self, game: Minesweeper):
        """
        Initialise le solveur avec une instance de jeu.
        
        Args:
            game: Instance du jeu Démineur à résoudre
        """
        self.game = game
        self.width = game.width
        self.height = game.height
        self.safe_cells: Set[Tuple[int, int]] = set()
        self.mine_cells: Set[Tuple[int, int]] = set()
    
    def solve(self) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """
        Résout le problème du Démineur en utilisant des règles simples.
        
        Returns:
            Tuple contenant deux ensembles: les cellules sûres et les cellules avec mines
        """
        start_time = time.time()
        
        # Réinitialiser les résultats
        self.safe_cells = set()
        self.mine_cells = set()
        
        board = self.game.get_visible_board()
        revealed_cells = self.game.revealed_cells
        
        # Règle 1: Pour chaque cellule révélée, si le nombre de cellules adjacentes inconnues est égal
        # au nombre de mines adjacentes, alors toutes ces cellules inconnues contiennent des mines
        for row, col in revealed_cells:
            value = board[row, col]
            if value > 0:  # Si la cellule a des mines adjacentes
                unknown_adjacent = self.game.get_unknown_adjacent_cells(row, col)
                flagged_adjacent = [(r, c) for r, c in unknown_adjacent if board[r, c] == Minesweeper.FLAG]
                
                # Si le nombre de cellules inconnues restantes correspond exactement au nombre de mines attendues
                if value == len(flagged_adjacent) + (len(unknown_adjacent) - len(flagged_adjacent)):
                    for r, c in unknown_adjacent:
                        if board[r, c] != Minesweeper.FLAG:
                            self.mine_cells.add((r, c))
        
        # Règle 2: Pour chaque cellule révélée, si le nombre de drapeaux adjacents est égal
        # au nombre de mines adjacentes, alors toutes les autres cellules adjacentes sont sûres
        for row, col in revealed_cells:
            value = board[row, col]
            if value > 0:  # Si la cellule a des mines adjacentes
                unknown_adjacent = self.game.get_unknown_adjacent_cells(row, col)
                flagged_adjacent = [(r, c) for r, c in unknown_adjacent if board[r, c] == Minesweeper.FLAG]
                
                # Si le nombre de drapeaux correspond exactement au nombre de mines attendues
                if value == len(flagged_adjacent):
                    for r, c in unknown_adjacent:
                        if board[r, c] != Minesweeper.FLAG:
                            self.safe_cells.add((r, c))
        
        elapsed_time = time.time() - start_time
        print(f"Résolution simple terminée en {elapsed_time:.2f} secondes.")
        print(f"Cellules sûres trouvées: {len(self.safe_cells)}")
        print(f"Mines identifiées: {len(self.mine_cells)}")
        
        return self.safe_cells, self.mine_cells
    
    def update_game(self, auto_play: bool = False) -> bool:
        """
        Met à jour le jeu avec les résultats de l'analyse.
        
        Args:
            auto_play: Si True, joue automatiquement les cellules sûres
            
        Returns:
            True si le jeu a été mis à jour, False sinon
        """
        updated = False
        board = self.game.get_visible_board()  # Get current board state
        
        # Marquer les mines avec des drapeaux
        for row, col in self.mine_cells:
            if board[row, col] == Minesweeper.UNKNOWN:
                self.game.toggle_flag(row, col)
                updated = True
        
        # Révéler les cellules sûres
        if auto_play:
            for row, col in self.safe_cells:
                if board[row, col] == Minesweeper.UNKNOWN:
                    self.game.reveal(row, col)
                    updated = True
                    
        return updated 