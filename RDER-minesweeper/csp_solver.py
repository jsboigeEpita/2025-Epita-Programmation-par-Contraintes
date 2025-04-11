import time
import numpy as np
from typing import Tuple, List, Set, Dict, Optional
from minesweeper import Minesweeper
import constraint
from itertools import combinations

class MinesweeperCSPSolver:
    """
    Solveur de Démineur utilisant la programmation par contraintes avec python-constraint.
    """
    
    def __init__(self, game: Minesweeper, logger=None):
        """
        Initialise le solveur avec une instance de jeu.
        
        Args:
            game: Instance du jeu Démineur à résoudre
            logger: Fonction de log personnalisée (par défaut, print)
        """
        self.game = game
        self.logger = logger if logger else print
        self.width = game.width
        self.height = game.height
        self.board = game.get_visible_board()
        self.num_mines = game.num_mines
        self.unknown_cells = set()
        self.update_unknown_cells()
        self.safe_cells: Set[Tuple[int, int]] = set()
        self.mine_cells: Set[Tuple[int, int]] = set()
        self.cached_solutions = None
        self.last_board_state = None
        
    def update_unknown_cells(self):
        """Met à jour l'ensemble des cellules inconnues"""
        self.unknown_cells.clear()
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col] == Minesweeper.UNKNOWN or self.board[row, col] == Minesweeper.FLAG:
                    self.unknown_cells.add((row, col))

    def get_border_cells(self) -> Set[Tuple[int, int]]:
        """Retourne les cellules non révélées adjacentes à des cellules révélées"""
        border_cells = set()
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col] >= 0:  # Cellule révélée avec un nombre
                    adjacent_cells = self.game.get_unknown_adjacent_cells(row, col)
                    border_cells.update(adjacent_cells)
        return border_cells

    def apply_simple_rules(self) -> bool:
        """Applique des règles simples avant d'utiliser le CSP"""
        updated = False
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col] >= 0:  # Cellule révélée avec un nombre
                    value = self.board[row, col]
                    adjacent_cells = self.game.get_unknown_adjacent_cells(row, col)
                    flagged = sum(1 for r, c in adjacent_cells if self.board[r, c] == Minesweeper.FLAG)
                    unknown = [(r, c) for r, c in adjacent_cells if self.board[r, c] == Minesweeper.UNKNOWN]

                    # Règle 1: Si le nombre = mines restantes, toutes les cellules inconnues sont des mines
                    if value - flagged == len(unknown):
                        self.mine_cells.update(unknown)
                        updated = True

                    # Règle 2: Si le nombre = drapeaux, toutes les autres cellules sont sûres
                    if value == flagged and unknown:
                        self.safe_cells.update(unknown)
                        updated = True

        return updated

    def solve(self, use_probability: bool = True) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """Résout le problème du Démineur"""
        start_time = time.time()
        self.safe_cells.clear()
        self.mine_cells.clear()
        
        # Mettre à jour l'état du plateau
        self.board = self.game.get_visible_board()
        self.update_unknown_cells()
        
        # Vérifier si l'état du plateau a changé depuis la dernière résolution
        current_board_state = self.board.tobytes()
        if current_board_state == self.last_board_state:
            return set(), set()
        self.last_board_state = current_board_state

        # Appliquer d'abord les règles simples
        if self.apply_simple_rules():
            self.logger("✨ Solutions trouvées avec les règles simples")
            return self.safe_cells, self.mine_cells

        # Si pas de cellules inconnues, retourner les ensembles vides
        if not self.unknown_cells:
            return self.safe_cells, self.mine_cells

        # Optimisation : ne considérer que les cellules frontalières
        border_cells = self.get_border_cells()
        if not border_cells:
            # Si pas de cellules frontalières, utiliser une approche probabiliste
            if use_probability:
                return self.solve_with_probability()
            return set(), set()

        # Créer le problème CSP
        problem = constraint.Problem()
        
        # Variables: une par cellule frontalière
        for row, col in border_cells:
            problem.addVariable(f"cell_{row}_{col}", [0, 1])

        # Contrainte: nombre total de mines restantes
        mines_remaining = self.num_mines - len(self.game.flagged_cells)
        if mines_remaining > 0:
            problem.addConstraint(
                constraint.MaxSumConstraint(mines_remaining),
                [f"cell_{row}_{col}" for row, col in border_cells]
            )

        # Contraintes pour chaque cellule révélée
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col] >= 0:
                    adjacent_cells = set(self.game.get_unknown_adjacent_cells(row, col)) & border_cells
                    if adjacent_cells:
                        value = self.board[row, col]
                        flagged_adjacent = sum(1 for r, c in self.game.get_adjacent_cells(row, col)
                                            if (r, c) in self.game.flagged_cells)
                        remaining_mines = value - flagged_adjacent
                        
                        adjacent_vars = [f"cell_{r}_{c}" for r, c in adjacent_cells]
                        if adjacent_vars:
                            problem.addConstraint(
                                constraint.ExactSumConstraint(remaining_mines),
                                adjacent_vars
                            )

        # Obtenir les solutions
        solutions = problem.getSolutions()
        if not solutions:
            self.logger("⚠️ Aucune solution trouvée avec CSP")
            return self.solve_with_probability() if use_probability else (set(), set())

        # Analyser les solutions
        mine_counts = {}
        for cell in border_cells:
            row, col = cell
            var_name = f"cell_{row}_{col}"
            count = sum(sol[var_name] for sol in solutions)
            prob = count / len(solutions)
            
            if prob == 0:
                self.safe_cells.add(cell)
            elif prob == 1:
                self.mine_cells.add(cell)
            else:
                mine_counts[cell] = prob

        # Si aucune cellule sûre/mine trouvée et probabilités activées
        if not self.safe_cells and not self.mine_cells and use_probability:
            if mine_counts:
                # Trouver la cellule la plus sûre
                safest_cell = min(mine_counts.items(), key=lambda x: x[1])
                if safest_cell[1] < 0.3:
                    self.safe_cells.add(safest_cell[0])
                
                # Identifier les mines probables
                for cell, prob in mine_counts.items():
                    if prob > 0.9:
                        self.mine_cells.add(cell)

        elapsed_time = time.time() - start_time
        self.logger(f"⏱️ Résolution terminée en {elapsed_time:.2f} secondes")
        self.logger(f"🎯 Cellules sûres: {len(self.safe_cells)}")
        self.logger(f"💣 Mines identifiées: {len(self.mine_cells)}")
        
        return self.safe_cells, self.mine_cells

    def solve_with_probability(self) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """Résout en utilisant une approche probabiliste quand CSP ne trouve pas de solution"""
        probabilities = self.calculate_probabilities()
        safe_cells = set()
        mine_cells = set()

        if probabilities:
            # Identifier les cellules les plus sûres et les plus dangereuses
            for cell, prob in probabilities.items():
                if prob < 0.1:  # Très faible probabilité d'être une mine
                    safe_cells.add(cell)
                elif prob > 0.9:  # Très forte probabilité d'être une mine
                    mine_cells.add(cell)

        return safe_cells, mine_cells

    def calculate_probabilities(self) -> Dict[Tuple[int, int], float]:
        """Calcule les probabilités de mines pour chaque cellule non révélée"""
        probabilities = {}
        total_unknown = len(self.unknown_cells)
        if total_unknown == 0:
            return probabilities

        mines_remaining = self.num_mines - len(self.game.flagged_cells)
        base_probability = mines_remaining / total_unknown

        for row, col in self.unknown_cells:
            prob = base_probability
            adjacent_revealed = []
            
            # Vérifier les cellules adjacentes révélées
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        if self.board[nr, nc] >= 0:
                            adjacent_revealed.append((nr, nc))

            if adjacent_revealed:
                # Ajuster la probabilité en fonction des cellules adjacentes
                local_prob = 0
                weight = 0
                for r, c in adjacent_revealed:
                    value = self.board[r, c]
                    unknown_adjacent = len(self.game.get_unknown_adjacent_cells(r, c))
                    if unknown_adjacent > 0:
                        local_prob += value / unknown_adjacent
                        weight += 1
                
                if weight > 0:
                    prob = (local_prob / weight + base_probability) / 2
            
            probabilities[(row, col)] = min(max(prob, 0), 1)  # Normaliser entre 0 et 1

        return probabilities

    def update_game(self, auto_play: bool = False) -> bool:
        """Met à jour le jeu avec les résultats de l'analyse"""
        updated = False
        board = self.game.get_visible_board()

        # Placer les drapeaux sur les mines
        for row, col in self.mine_cells:
            if board[row, col] == Minesweeper.UNKNOWN:
                self.game.toggle_flag(row, col)
                self.logger(f"🚩 Drapeau placé en ({row}, {col})")
                updated = True

        # Révéler les cellules sûres
        if auto_play:
            for row, col in self.safe_cells:
                if board[row, col] == Minesweeper.UNKNOWN:
                    self.game.reveal(row, col)
                    self.logger(f"🔓 Révélation de la cellule ({row}, {col})")
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
            self.unknown_cells = set()
            self.update_unknown_cells()
        
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