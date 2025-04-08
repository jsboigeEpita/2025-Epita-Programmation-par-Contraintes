import numpy as np
import random
import matplotlib.pyplot as plt
from typing import Tuple, List, Set, Optional

class Minesweeper:
    """
    Classe représentant le jeu du Démineur.
    Cette implémentation permet de générer des grilles aléatoires
    ou de charger des configurations prédéfinies pour tester le solveur.
    """
    
    # Constantes pour représenter l'état des cases
    UNKNOWN = -1  # Case non révélée
    MINE = -2     # Mine (pour la grille de solution)
    FLAG = -3     # Drapeau placé par le joueur/solveur
    
    def __init__(self, width: int, height: int, num_mines: int):
        """
        Initialise une nouvelle partie de Démineur.
        
        Args:
            width: Largeur de la grille
            height: Hauteur de la grille
            num_mines: Nombre de mines à placer
        """
        self.width = width
        self.height = height
        self.num_mines = min(num_mines, width * height - 1)
        
        # Grille visible par le joueur/solveur (UNKNOWN, FLAG ou valeurs numériques 0-8)
        self.board = np.full((height, width), self.UNKNOWN, dtype=int)
        
        # Grille de solution (emplacements des mines)
        self.solution = np.zeros((height, width), dtype=int)
        
        # État du jeu
        self.game_over = False
        self.win = False
        
        # Positions des cases révélées
        self.revealed_cells = set()
        
        # Drapeaux placés
        self.flagged_cells = set()
        
    def initialize_mines(self, first_click: Tuple[int, int] = None):
        """
        Place aléatoirement les mines sur la grille,
        en évitant la position du premier clic.
        
        Args:
            first_click: Position (row, col) du premier clic, à éviter
        """
        # Reset la grille de solution
        self.solution = np.zeros((self.height, self.width), dtype=int)
        
        # Liste des positions possibles pour les mines
        positions = [(r, c) for r in range(self.height) for c in range(self.width)]
        
        # Enlever la position du premier clic et son voisinage si spécifiée
        if first_click is not None:
            r, c = first_click
            safe_positions = {(r+dr, c+dc) for dr in range(-1, 2) for dc in range(-1, 2)
                             if 0 <= r+dr < self.height and 0 <= c+dc < self.width}
            positions = [pos for pos in positions if pos not in safe_positions]
        
        # Sélectionner aléatoirement les positions des mines
        mine_positions = random.sample(positions, min(self.num_mines, len(positions)))
        
        # Placer les mines
        for r, c in mine_positions:
            self.solution[r, c] = self.MINE
            
    def count_adjacent_mines(self, row: int, col: int) -> int:
        """
        Compte le nombre de mines adjacentes à une case.
        
        Args:
            row: Ligne de la case
            col: Colonne de la case
            
        Returns:
            Nombre de mines adjacentes
        """
        count = 0
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < self.height and 0 <= c < self.width and self.solution[r, c] == self.MINE:
                    count += 1
        return count
    
    def reveal(self, row: int, col: int) -> bool:
        """
        Révèle une case de la grille.
        
        Args:
            row: Ligne de la case
            col: Colonne de la case
            
        Returns:
            True si la révélation est réussie, False si partie perdue
        """
        if self.game_over:
            return False
        
        if not (0 <= row < self.height and 0 <= col < self.width):
            return False
        
        # Case déjà révélée ou marquée d'un drapeau
        if (row, col) in self.revealed_cells or self.board[row, col] == self.FLAG:
            return True
        
        # Si on clique sur une mine, partie perdue
        if self.solution[row, col] == self.MINE:
            self.board[row, col] = self.MINE
            self.game_over = True
            return False
        
        # Calculer le nombre de mines adjacentes
        adjacent_mines = self.count_adjacent_mines(row, col)
        self.board[row, col] = adjacent_mines
        self.revealed_cells.add((row, col))
        
        # Si aucune mine adjacente, révéler automatiquement les cases voisines
        if adjacent_mines == 0:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if dr == 0 and dc == 0:
                        continue
                    r, c = row + dr, col + dc
                    if 0 <= r < self.height and 0 <= c < self.width and (r, c) not in self.revealed_cells:
                        self.reveal(r, c)
        
        # Vérifier si partie gagnée
        if len(self.revealed_cells) == self.width * self.height - self.num_mines:
            self.win = True
            self.game_over = True
        
        return True
    
    def toggle_flag(self, row: int, col: int) -> bool:
        """
        Place ou retire un drapeau sur une case.
        
        Args:
            row: Ligne de la case
            col: Colonne de la case
            
        Returns:
            True si l'opération est réussie
        """
        if self.game_over:
            return False
        
        if not (0 <= row < self.height and 0 <= col < self.width):
            return False
        
        # Ne peut pas placer de drapeau sur une case révélée
        if (row, col) in self.revealed_cells:
            return False
        
        # Retirer le drapeau s'il existe déjà
        if (row, col) in self.flagged_cells:
            self.flagged_cells.remove((row, col))
            self.board[row, col] = self.UNKNOWN
        else:
            # Placer un drapeau
            self.flagged_cells.add((row, col))
            self.board[row, col] = self.FLAG
        
        return True
    
    def get_visible_board(self) -> np.ndarray:
        """
        Retourne la grille visible par le joueur/solveur.
        
        Returns:
            Grille visible (numpy array)
        """
        return self.board.copy()
    
    def get_solution(self) -> np.ndarray:
        """
        Retourne la grille de solution (avec les mines).
        
        Returns:
            Grille de solution (numpy array)
        """
        return self.solution.copy()
    
    def get_unrevealed_count(self) -> int:
        """
        Retourne le nombre de cases non révélées.
        
        Returns:
            Nombre de cases non révélées
        """
        return self.width * self.height - len(self.revealed_cells)
    
    def get_adjacent_cells(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Retourne les coordonnées des cases adjacentes à une position donnée.
        
        Args:
            row: Ligne de la position
            col: Colonne de la position
            
        Returns:
            Liste de tuples (row, col) des cases adjacentes
        """
        adjacent = []
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < self.height and 0 <= c < self.width:
                    adjacent.append((r, c))
        return adjacent
    
    def get_unknown_adjacent_cells(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Retourne les coordonnées des cases adjacentes non révélées.
        
        Args:
            row: Ligne de la position
            col: Colonne de la position
            
        Returns:
            Liste de tuples (row, col) des cases adjacentes non révélées
        """
        return [(r, c) for r, c in self.get_adjacent_cells(row, col) 
                if (r, c) not in self.revealed_cells]
    
    def display(self, show_mines: bool = False):
        """
        Affiche graphiquement la grille de jeu.
        
        Args:
            show_mines: Si True, affiche également les mines (pour le debug)
        """
        plt.figure(figsize=(self.width/2, self.height/2))
        
        # Créer une grille à afficher
        display_board = self.board.copy()
        
        # Si demandé, afficher les mines sur les cases non révélées
        if show_mines:
            for r in range(self.height):
                for c in range(self.width):
                    if display_board[r, c] == self.UNKNOWN and self.solution[r, c] == self.MINE:
                        display_board[r, c] = self.MINE
        
        # Configuration des couleurs
        cmap = plt.cm.viridis
        norm = plt.Normalize(vmin=-3, vmax=8)
        
        # Afficher la grille
        plt.imshow(display_board, cmap=cmap, norm=norm)
        
        # Ajouter les valeurs numériques
        for r in range(self.height):
            for c in range(self.width):
                cell_value = display_board[r, c]
                if cell_value >= 0:
                    plt.text(c, r, str(cell_value), ha='center', va='center', 
                             fontweight='bold', color='white' if cell_value > 0 else 'black')
                elif cell_value == self.FLAG:
                    plt.text(c, r, '🚩', ha='center', va='center')
                elif cell_value == self.MINE:
                    plt.text(c, r, '💣', ha='center', va='center')
                elif cell_value == self.UNKNOWN:
                    plt.text(c, r, '?', ha='center', va='center', color='white')
        
        # Ajouter une grille
        plt.grid(True, color='black', linestyle='-', linewidth=1)
        plt.xticks(np.arange(-0.5, self.width, 1), [])
        plt.yticks(np.arange(-0.5, self.height, 1), [])
        
        plt.title('Démineur')
        plt.tight_layout()
        plt.show()
    
    @classmethod
    def from_string(cls, board_str: str) -> 'Minesweeper':
        """
        Crée une instance de Minesweeper à partir d'une représentation textuelle.
        Format: '*' pour une mine, '?' pour une case inconnue, chiffres 0-8 pour les cases révélées
        
        Args:
            board_str: Représentation textuelle de la grille
            
        Returns:
            Instance de Minesweeper
        """
        # Nettoyer les lignes (enlever les espaces et lignes vides)
        lines = [line.strip() for line in board_str.strip().split('\n') if line.strip()]
        height = len(lines)
        
        if height == 0:
            raise ValueError("La grille est vide")
            
        # Vérifier que toutes les lignes ont la même longueur
        width = len(lines[0])
        for i, line in enumerate(lines):
            if len(line) != width:
                raise ValueError(f"La ligne {i+1} a une longueur différente ({len(line)}) de la première ligne ({width})")
        
        # Compter les mines
        num_mines = sum(line.count('*') for line in lines)
        
        game = cls(width, height, num_mines)
        
        # Configurer la solution
        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                if char == '*':
                    game.solution[r, c] = cls.MINE
        
        # Calculer la grille visible
        for r in range(height):
            for c in range(width):
                if lines[r][c] != '*' and lines[r][c] != '?':
                    value = int(lines[r][c])
                    game.board[r, c] = value
                    game.revealed_cells.add((r, c))
        
        return game 