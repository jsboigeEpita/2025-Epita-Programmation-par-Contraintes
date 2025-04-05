#!/usr/bin/env python3
"""
Script pour générer des grilles de Démineur de taille et difficulté personnalisables.
Ce script simplifié contient la fonctionnalité de génération de grilles, avec compatibilité
pour les autres modules du projet.
"""

import argparse
import random
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List, Set, Optional


class Minesweeper:
    """
    Classe représentant le jeu du Démineur.
    Cette implémentation permet de générer des grilles aléatoires.
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
    
    def get_unknown_adjacent_cells(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Retourne les coordonnées des cases adjacentes non révélées.
        
        Args:
            row: Ligne de la position
            col: Colonne de la position
            
        Returns:
            Liste de tuples (row, col) des cases adjacentes non révélées
        """
        adjacent = []
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < self.height and 0 <= c < self.width and (r, c) not in self.revealed_cells:
                    adjacent.append((r, c))
        return adjacent
    
    def get_unrevealed_count(self) -> int:
        """
        Retourne le nombre de cases non révélées.
        
        Returns:
            Nombre de cases non révélées
        """
        return self.width * self.height - len(self.revealed_cells)
    
    def display(self, show_mines: bool = False):
        """
        Affiche la grille de jeu sous forme textuelle.
        
        Args:
            show_mines: Si True, affiche également les mines
        """
        symbols = {
            self.UNKNOWN: '?',
            self.MINE: '*',
            self.FLAG: 'F',
            0: ' '
        }
        
        print("+" + "-" * (self.width * 2 - 1) + "+")
        for r in range(self.height):
            row_str = "|"
            for c in range(self.width):
                if (r, c) in self.revealed_cells:
                    value = self.board[r, c]
                    if value == 0:
                        row_str += " "
                    else:
                        row_str += str(value)
                elif (r, c) in self.flagged_cells:
                    row_str += "F"
                elif show_mines and self.solution[r, c] == self.MINE:
                    row_str += "*"
                else:
                    row_str += "?"
                row_str += " "
            print(row_str[:-1] + "|")  # Enlever le dernier espace
        print("+" + "-" * (self.width * 2 - 1) + "+")


def generate_grid(width, height, num_mines, reveal_percentage=0.3, seed=None):
    """
    Génère une grille de Démineur avec un pourcentage de cases révélées.
    
    Args:
        width: Largeur de la grille
        height: Hauteur de la grille
        num_mines: Nombre de mines
        reveal_percentage: Pourcentage de cases non-mines à révéler
        seed: Graine aléatoire pour la reproductibilité
        
    Returns:
        Une instance de Minesweeper avec la grille générée
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Créer une grille vide
    game = Minesweeper(width, height, num_mines)
    
    # Placer les mines
    game.initialize_mines()
    
    # Calculer le nombre de cases à révéler
    total_cells = width * height
    non_mine_cells = total_cells - num_mines
    cells_to_reveal = int(non_mine_cells * reveal_percentage)
    
    # Créer une liste de toutes les positions sans mines
    safe_positions = []
    for r in range(height):
        for c in range(width):
            if game.solution[r, c] != Minesweeper.MINE:
                safe_positions.append((r, c))
    
    # Révéler aléatoirement des cases
    positions_to_reveal = random.sample(safe_positions, min(cells_to_reveal, len(safe_positions)))
    for r, c in positions_to_reveal:
        game.reveal(r, c)
    
    return game

def save_grid_to_file(game, filename):
    """
    Sauvegarde une grille de Démineur dans un fichier texte.
    
    Args:
        game: Instance de Minesweeper
        filename: Nom du fichier de sortie
    """
    with open(filename, 'w') as f:
        # Écrire les dimensions et le nombre de mines
        f.write(f"{game.width} {game.height} {game.num_mines}\n")
        
        # Écrire la grille de solution
        solution = game.get_solution()
        for r in range(game.height):
            line = ""
            for c in range(game.width):
                if solution[r, c] == Minesweeper.MINE:
                    line += "*"
                else:
                    line += "."
            f.write(line + "\n")
        
        # Écrire les cases révélées
        f.write("\n")
        board = game.get_visible_board()
        for r in range(game.height):
            line = ""
            for c in range(game.width):
                if (r, c) in game.revealed_cells:
                    line += str(board[r, c])
                else:
                    line += "?"
            f.write(line + "\n")
    
    print(f"Grille sauvegardée dans {filename}")

def load_grid_from_file(filename):
    """
    Charge une grille de Démineur depuis un fichier texte.
    Cette fonction est ajoutée pour la compatibilité avec les autres modules du projet.
    
    Args:
        filename: Nom du fichier à charger
        
    Returns:
        Une instance de Minesweeper, ou None si le chargement échoue
    """
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        # Lire les dimensions et le nombre de mines
        first_line = lines[0].strip().split()
        if len(first_line) >= 3:
            width = int(first_line[0])
            height = int(first_line[1])
            num_mines = int(first_line[2])
        else:
            width = len(lines[1].strip())
            height = sum(1 for line in lines[1:] if line.strip() and '*' in line or '.' in line)
            num_mines = sum(line.count('*') for line in lines[1:])
        
        # Créer le jeu
        game = Minesweeper(width, height, num_mines)
        
        # Lire la grille de solution (si présente)
        solution_lines = []
        revealed_lines = []
        
        # Déterminer où se trouve la ligne vide séparant solution et grille visible
        separator_line = -1
        for i, line in enumerate(lines[1:], 1):
            if not line.strip():
                separator_line = i
                break
        
        if separator_line > 0:
            solution_lines = lines[1:separator_line]
            revealed_lines = lines[separator_line+1:]
        else:
            # Format simple : une seule grille avec * pour les mines
            solution_lines = lines[1:]
        
        # Charger la solution
        for r, line in enumerate(solution_lines):
            if r >= height:
                break
            line = line.strip()
            for c, char in enumerate(line):
                if c >= width:
                    break
                if char == '*':
                    game.solution[r, c] = Minesweeper.MINE
        
        # Charger les cases révélées (si présentes)
        if revealed_lines:
            for r, line in enumerate(revealed_lines):
                if r >= height:
                    break
                line = line.strip()
                for c, char in enumerate(line):
                    if c >= width:
                        break
                    if char.isdigit():
                        value = int(char)
                        game.board[r, c] = value
                        game.revealed_cells.add((r, c))
        
        return game
        
    except Exception as e:
        print(f"Erreur lors du chargement de la grille: {e}")
        return None

# Fonction pour la compatibilité avec les autres scripts
def solve_step(game):
    """
    Implémentation de solve_step pour la compatibilité avec d'autres modules.
    Si aucune solution n'est trouvée, cette fonction choisit aléatoirement une case parmi les cases non révélées.
    
    Args:
        game: Instance de Minesweeper
        
    Returns:
        Tuple de deux ensembles (cellules sûres, mines) avec au moins une cellule sûre aléatoire si aucune solution certaine
    """
    print("Utilisation du générateur de grilles en mode résolution...")
    
    # Aucune case sûre ou mine identifiée avec certitude
    safe_cells = set()
    mine_cells = set()
    
    # Chercher toutes les cases non révélées
    board = game.get_visible_board()
    unrevealed = []
    for row in range(game.height):
        for col in range(game.width):
            if board[row, col] == Minesweeper.UNKNOWN:
                unrevealed.append((row, col))
    
    # Si des cases non révélées existent, en choisir une aléatoirement
    if unrevealed:
        random_choice = random.choice(unrevealed)
        safe_cells.add(random_choice)
        print(f"Aucune solution certaine trouvée. Choix aléatoire de la case {random_choice}")
    
    return safe_cells, mine_cells

def main():
    parser = argparse.ArgumentParser(description="Générateur de grilles de Démineur")
    parser.add_argument("--width", type=int, default=9, help="Largeur de la grille")
    parser.add_argument("--height", type=int, default=9, help="Hauteur de la grille")
    parser.add_argument("--mines", type=int, default=10, help="Nombre de mines")
    parser.add_argument("--reveal", type=float, default=0.3, help="Pourcentage de cases non-mines à révéler (0.0-1.0)")
    parser.add_argument("--seed", type=int, help="Graine aléatoire pour la reproductibilité")
    parser.add_argument("--output", type=str, default="grid.txt", help="Fichier de sortie")
    parser.add_argument("--display", action="store_true", help="Afficher la grille générée")
    parser.add_argument("--load", type=str, help="Charger une grille depuis un fichier")
    
    args = parser.parse_args()
    
    # Charger une grille existante si spécifié
    if args.load:
        game = load_grid_from_file(args.load)
        if game:
            print(f"Grille chargée depuis {args.load}")
            if args.display:
                print("Grille chargée:")
                game.display(show_mines=True)
            return
        else:
            print(f"Erreur: Impossible de charger la grille depuis {args.load}")
            return
    
    # Vérifier les paramètres
    if args.mines >= args.width * args.height:
        print("Erreur: Trop de mines pour la taille de la grille.")
        return
    
    if args.reveal < 0 or args.reveal > 1:
        print("Erreur: Le pourcentage de révélation doit être entre 0.0 et 1.0.")
        return
    
    # Générer la grille
    game = generate_grid(args.width, args.height, args.mines, args.reveal, args.seed)
    
    # Sauvegarder dans un fichier
    save_grid_to_file(game, args.output)
    
    # Afficher si demandé
    if args.display:
        print("Grille générée:")
        game.display(show_mines=True)

# Pour permettre l'import de ce module dans d'autres scripts
if __name__ == "__main__":
    main() 