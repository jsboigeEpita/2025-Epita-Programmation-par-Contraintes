#!/usr/bin/env python3
"""
Script pour générer des grilles de Démineur de taille et difficulté personnalisables.
"""

import argparse
import random
import numpy as np
from minesweeper import Minesweeper

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
        board = game.get_visible_board()
        solution = game.get_solution()
        
        for r in range(game.height):
            line = ""
            for c in range(game.width):
                if (r, c) in game.revealed_cells:
                    line += str(board[r, c])
                elif solution[r, c] == Minesweeper.MINE:
                    line += "*"
                else:
                    line += "?"
            f.write(line + "\n")
    
    print(f"Grille sauvegardée dans {filename}")

def main():
    parser = argparse.ArgumentParser(description="Générateur de grilles de Démineur")
    parser.add_argument("--width", type=int, default=8, help="Largeur de la grille")
    parser.add_argument("--height", type=int, default=8, help="Hauteur de la grille")
    parser.add_argument("--mines", type=int, default=10, help="Nombre de mines")
    parser.add_argument("--reveal", type=float, default=0.3, help="Pourcentage de cases non-mines à révéler (0.0-1.0)")
    parser.add_argument("--seed", type=int, help="Graine aléatoire pour la reproductibilité")
    parser.add_argument("--output", type=str, default="grid.txt", help="Fichier de sortie")
    parser.add_argument("--display", action="store_true", help="Afficher la grille générée")
    
    args = parser.parse_args()
    
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

if __name__ == "__main__":
    main() 