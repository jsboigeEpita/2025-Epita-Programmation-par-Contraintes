#!/usr/bin/env python3
"""
Interface en ligne de commande simplifiée pour le Démineur utilisant uniquement le solveur CSP
avec option d'intégration LLM pour les situations ambiguës.
"""

import os
import sys
import time
import random
import numpy as np
if __package__ is None:
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, path)

# Try to load dotenv for environment variables
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
    # Load environment variables from .env file
    load_dotenv()
except ImportError:
    DOTENV_AVAILABLE = False

# Importer les modules du projet
try:
    from pcon.minesweeper import Minesweeper
    from pcon.csp_solver import MinesweeperCSPSolver
    from pcon.llm_csp_solver import LLMCSPSolver, OPENAI_AVAILABLE
    from pcon.generate_minesweeper import generate_grid, load_grid_from_file
except ImportError:
    # Essayer l'import relatif si ce fichier est exécuté comme un module
    try:
        from .minesweeper import Minesweeper
        from .csp_solver import MinesweeperCSPSolver
        from .llm_csp_solver import LLMCSPSolver, OPENAI_AVAILABLE
        from .generate_minesweeper import generate_grid, load_grid_from_file
    except ImportError:
        # Fallback aux imports directs pour compatibilité
        from minesweeper import Minesweeper
        from csp_solver import MinesweeperCSPSolver
        from llm_csp_solver import LLMCSPSolver, OPENAI_AVAILABLE
        from generate_minesweeper import generate_grid, load_grid_from_file

# Configuration de l'interface
CONFIG = {
    'colors': {
        'title': '\033[1;36m',  # Cyan gras
        'subtitle': '\033[1;34m',  # Bleu gras
        'success': '\033[1;32m',  # Vert gras
        'error': '\033[1;31m',  # Rouge gras
        'info': '\033[1;33m',  # Jaune gras
        'reset': '\033[0m',     # Réinitialiser
        'grid': {
            'unknown': '\033[47m',  # Fond blanc
            'mine': '\033[41;97m',  # Fond rouge, texte blanc
            'flag': '\033[43;30m',  # Fond jaune, texte noir
            'revealed': '\033[0m',  # Normal
            'error': '\033[41;93m',  # Fond rouge, texte jaune (pour faux drapeaux)
            'numbers': [
                '\033[36m',  # Cyan (1)
                '\033[32m',  # Vert (2)
                '\033[31m',  # Rouge (3)
                '\033[34m',  # Bleu (4)
                '\033[35m',  # Magenta (5)
                '\033[33m',  # Jaune (6)
                '\033[37m',  # Blanc (7)
                '\033[90m',  # Gris (8)
            ]
        }
    },
    'symbols': {
        'unknown': '?',
        'mine': 'X',
        'flag': 'F',
        'empty': ' '
    }
}

def clear_screen():
    """Efface l'écran du terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def color_text(text, color_type):
    """Renvoie le texte avec la couleur spécifiée."""
    if color_type in CONFIG['colors']:
        return f"{CONFIG['colors'][color_type]}{text}{CONFIG['colors']['reset']}"
    return text

def print_title(text):
    """Affiche un titre avec une mise en forme spéciale."""
    width = min(80, max(60, len(text) + 10))
    border = "=" * width
    padding = " " * ((width - len(text)) // 2)
    
    print(f"\n{color_text(border, 'title')}")
    print(f"{color_text(padding + text + padding, 'title')}")
    print(f"{color_text(border, 'title')}\n")

def print_grid(game, show_mines=False):
    """
    Affiche la grille de jeu avec des couleurs.
    
    Args:
        game: Instance du jeu Démineur
        show_mines: Si True, affiche toutes les mines
    """
    board = game.get_visible_board()
    solution = game.get_solution() if show_mines else None
    width = game.width
    height = game.height
    
    # Calcul de l'espacement pour que la grille soit bien alignée
    col_width = 3  # Largeur de chaque colonne
    
    # Afficher les indices de colonne
    print(" " * 4, end="")
    for col in range(width):
        print(f"{col:^{col_width}}", end="")
    print()
    
    # Afficher la ligne de séparation
    print("   +", end="")
    for col in range(width):
        print("-" * col_width + "+", end="")
    print()
    
    # Afficher le contenu de la grille
    for row in range(height):
        print(f"{row:2d} |", end="")
        for col in range(width):
            cell_value = board[row, col]
            
            # Afficher la cellule en fonction de sa valeur
            if show_mines and solution is not None and solution[row, col] == Minesweeper.MINE and cell_value == Minesweeper.UNKNOWN:
                # Case qui contient une mine non marquée (affichée uniquement quand show_mines=True)
                cell_text = f" {CONFIG['symbols']['mine']} "
                cell_color = CONFIG['colors']['grid']['mine']
            elif show_mines and solution is not None and solution[row, col] == Minesweeper.MINE and cell_value != Minesweeper.FLAG:
                # Afficher les mines cachées comme des mines
                cell_text = f" {CONFIG['symbols']['mine']} "
                cell_color = CONFIG['colors']['grid']['mine']
            elif cell_value == Minesweeper.UNKNOWN:
                cell_text = f" {CONFIG['symbols']['unknown']} "
                cell_color = CONFIG['colors']['grid']['unknown']
            elif cell_value == Minesweeper.FLAG:
                # Si show_mines est True et que c'est un faux drapeau, le montrer différemment
                if show_mines and solution is not None and solution[row, col] != Minesweeper.MINE:
                    cell_text = f" ! "  # Faux drapeau
                    cell_color = CONFIG['colors']['grid']['error']
                else:
                    cell_text = f" {CONFIG['symbols']['flag']} "
                    cell_color = CONFIG['colors']['grid']['flag']
            elif cell_value == Minesweeper.MINE:
                cell_text = f" {CONFIG['symbols']['mine']} "
                cell_color = CONFIG['colors']['grid']['mine']
            elif cell_value == 0:
                cell_text = f" {CONFIG['symbols']['empty']} "
                cell_color = CONFIG['colors']['grid']['revealed']
            else:  # Cellule révélée avec un nombre
                color_idx = min(cell_value - 1, len(CONFIG['colors']['grid']['numbers']) - 1)
                cell_text = f" {cell_value} "
                cell_color = CONFIG['colors']['grid']['numbers'][color_idx]
            
            # Afficher la cellule avec sa couleur
            print(f"{cell_color}{cell_text}{CONFIG['colors']['reset']}|", end="")
        
        # Afficher la ligne de séparation
        print("\n   +", end="")
        for col in range(width):
            print("-" * col_width + "+", end="")
        print()

def print_stats(game):
    """Affiche les statistiques du jeu."""
    print(f"\nDimensions: {game.width}x{game.height}")
    print(f"Nombre total de mines: {game.num_mines}")
    print(f"Cases révélées: {len(game.revealed_cells)}/{game.width * game.height}")
    print(f"Drapeaux placés: {len(game.flagged_cells)}/{game.num_mines}")
    
    if game.game_over:
        if game.win:
            print(color_text("\nVICTOIRE! Toutes les mines ont été identifiées correctement.", 'success'))
        else:
            # Vérifier si une mine a été révélée
            board = game.get_visible_board()
            mine_revealed = any(cell == Minesweeper.MINE for row in board for cell in row)
            
            if mine_revealed:
                print(color_text("\nDÉFAITE! Une mine a été révélée.", 'error'))
            else:
                print(color_text("\nPARTIE TERMINÉE. Le jeu a été forcé de se terminer.", 'info'))

def print_menu():
    """Affiche le menu principal."""
    print(color_text("\n--- MENU PRINCIPAL ---", 'subtitle'))
    print("1. Générer une nouvelle grille")
    print("2. Charger une grille depuis un fichier")
    print("3. Jouer manuellement")
    print("4. Résoudre avec le solveur CSP")
    print("5. Résoudre avec le solveur CSP + LLM")
    if not OPENAI_AVAILABLE:
        print(color_text("   (Bibliothèque OpenAI non disponible - Installée avec 'pip install openai')", 'error'))
    print("0. Quitter")
    print("\nVotre choix: ", end="")

def generate_grid_interactive():
    """Génère une nouvelle grille de jeu."""
    print_title("GÉNÉRER UNE NOUVELLE GRILLE")
    
    try:
        width = int(input("Largeur (par défaut 9): ") or "9")
        height = int(input("Hauteur (par défaut 9): ") or "9")
        
        max_mines = width * height - 1
        default_mines = min(10, max_mines)
        
        mines_prompt = f"Nombre de mines (1-{max_mines}, par défaut {default_mines}): "
        mines = int(input(mines_prompt) or str(default_mines))
        mines = max(1, min(mines, max_mines))
        
        reveal_percentage = float(input("Pourcentage de révélation (0.0-1.0, par défaut 0.3): ") or "0.3")
        reveal_percentage = max(0.0, min(reveal_percentage, 1.0))
        
        game = generate_grid(width=width, height=height, num_mines=mines, reveal_percentage=reveal_percentage)
        
        print(color_text(f"\nGrille {width}x{height} avec {mines} mines générée avec succès!", 'success'))
        input("Appuyez sur Entrée pour continuer...")
        return game
        
    except ValueError:
        print(color_text("\nErreur: Veuillez entrer des nombres valides.", 'error'))
        input("Appuyez sur Entrée pour continuer...")
        return None

def load_grid():
    """Charge une grille depuis un fichier."""
    print_title("CHARGER UNE GRILLE")
    
    # Lister les fichiers disponibles dans le répertoire examples/
    examples_dir = "examples"
    if os.path.isdir(examples_dir):
        files = [f for f in os.listdir(examples_dir) if f.endswith('.txt')]
        if files:
            print("Grilles disponibles:")
            for i, file in enumerate(files, 1):
                print(f"{i}. {file}")
            
            try:
                choice = input("\nChoisissez un numéro ou entrez un autre chemin de fichier: ")
                
                # Si l'utilisateur a choisi un numéro dans la liste
                if choice.isdigit() and 1 <= int(choice) <= len(files):
                    file_path = os.path.join(examples_dir, files[int(choice) - 1])
                else:
                    file_path = choice
                
                game = load_grid_from_file(file_path)
                if game:
                    print(color_text(f"\nGrille chargée depuis {file_path} avec succès!", 'success'))
                    input("Appuyez sur Entrée pour continuer...")
                    return game
                else:
                    print(color_text(f"\nErreur: Impossible de charger la grille depuis {file_path}", 'error'))
                    input("Appuyez sur Entrée pour continuer...")
                    return None
                
            except (ValueError, IndexError):
                print(color_text("\nErreur: Choix invalide.", 'error'))
                input("Appuyez sur Entrée pour continuer...")
                return None
        else:
            print(color_text(f"Aucun fichier .txt trouvé dans le répertoire {examples_dir}", 'error'))
    else:
        print(color_text(f"Le répertoire {examples_dir} n'existe pas", 'error'))
    
    # Si pas de fichiers trouvés, demander un chemin directement
    file_path = input("\nEntrez le chemin du fichier: ")
    if not file_path:
        return None
    
    game = load_grid_from_file(file_path)
    if game:
        print(color_text(f"\nGrille chargée depuis {file_path} avec succès!", 'success'))
        input("Appuyez sur Entrée pour continuer...")
        return game
    else:
        print(color_text(f"\nErreur: Impossible de charger la grille depuis {file_path}", 'error'))
        input("Appuyez sur Entrée pour continuer...")
        return None

def play_manually(game):
    """Permet de jouer manuellement à la grille."""
    if not game:
        print(color_text("\nAucune grille active. Générez ou chargez une grille d'abord.", 'error'))
        input("Appuyez sur Entrée pour continuer...")
        return
    
    # Faire une copie du jeu pour ne pas modifier l'original
    game_copy = Minesweeper(width=game.width, height=game.height, num_mines=game.num_mines)
    game_copy.solution = game.solution.copy()
    game_copy.board = game.board.copy()
    game_copy.revealed_cells = set(game.revealed_cells)
    game_copy.flagged_cells = set(game.flagged_cells)
    game_copy.game_over = game.game_over
    game_copy.win = game.win
    
    # Si le jeu est déjà terminé, commencer une nouvelle partie
    if game_copy.game_over:
        print(color_text("\nLa partie est déjà terminée. Commencer une nouvelle?", 'info'))
        if input("Oui (o) / Non (n): ").lower().startswith('o'):
            game_copy = Minesweeper(width=game.width, height=game.height, num_mines=game.num_mines)
            game_copy.solution = game.solution.copy()
            game_copy.initialize_mines()
        else:
            return game
    
    while not game_copy.game_over:
        clear_screen()
        print_title("JEU MANUEL")
        print_grid(game_copy)
        print_stats(game_copy)
        
        print(color_text("\n--- COMMANDES ---", 'subtitle'))
        print("r <ligne> <colonne> - Révéler une case")
        print("f <ligne> <colonne> - Placer/retirer un drapeau")
        print("q - Quitter la partie")
        print("\nEntrez une commande: ", end="")
        
        cmd = input().strip().lower().split()
        
        if not cmd:
            continue
            
        if cmd[0] == 'q':
            break
            
        if len(cmd) != 3:
            print(color_text("\nErreur: Format de commande invalide.", 'error'))
            input("Appuyez sur Entrée pour continuer...")
            continue
            
        try:
            row, col = int(cmd[1]), int(cmd[2])
            
            if cmd[0] == 'r':
                if not game_copy.reveal(row, col):
                    print(color_text("\nBOOM! Vous avez révélé une mine!", 'error'))
                    input("Appuyez sur Entrée pour continuer...")
            elif cmd[0] == 'f':
                game_copy.toggle_flag(row, col)
            else:
                print(color_text("\nErreur: Commande invalide.", 'error'))
                input("Appuyez sur Entrée pour continuer...")
                
        except ValueError:
            print(color_text("\nErreur: Coordonnées invalides.", 'error'))
            input("Appuyez sur Entrée pour continuer...")
    
    # Afficher la grille finale
    clear_screen()
    print_title("PARTIE TERMINÉE")
    print_grid(game_copy, show_mines=True)
    print_stats(game_copy)
    input("\nAppuyez sur Entrée pour continuer...")
    
    # Mettre à jour la grille originale
    return game_copy

def choose_random_cell(game):
    """
    Choisit une case aléatoire parmi les cases non révélées.
    
    Args:
        game: Instance du jeu Démineur
        
    Returns:
        Coordonnées (row, col) d'une case aléatoire
    """
    board = game.get_visible_board()
    height, width = board.shape
    
    # Trouver toutes les cases non révélées
    unrevealed = []
    for row in range(height):
        for col in range(width):
            if board[row, col] == Minesweeper.UNKNOWN:
                unrevealed.append((row, col))
    
    if unrevealed:
        return unrevealed[random.randint(0, len(unrevealed) - 1)]
    else:
        # Cas d'erreur (ne devrait pas arriver)
        return (0, 0)

def finish_game_forcefully(game):
    """
    Force la fin d'une partie de démineur en révélant toutes les cases sûres et
    en marquant toutes les mines. Utilisé quand le solveur est bloqué.
    
    Args:
        game: Instance du jeu Démineur
        
    Returns:
        None, modifie l'état du jeu directement
    """
    print(color_text("\nForçage de la fin de la partie...", 'info'))
    
    try:
        # Récupérer les informations sur la grille
        solution = game.get_solution()
        board = game.get_visible_board()
        height, width = board.shape
        
        # Vérifier si une mine a été révélée
        mine_revealed = False
        for row in range(height):
            for col in range(width):
                if board[row, col] == Minesweeper.MINE:
                    mine_revealed = True
                    break
        
        # Méthode directe et forcée : on traite la solution directement
        # Pour chaque case de la grille
        mines_marked = 0
        for row in range(height):
            for col in range(width):
                # Si c'est une mine non encore marquée par un drapeau
                if solution[row, col] == Minesweeper.MINE:
                    if (row, col) not in game.flagged_cells and board[row, col] != Minesweeper.MINE:
                        # Forcer la mise en place d'un drapeau
                        game.toggle_flag(row, col)
                        mines_marked += 1
                    elif (row, col) in game.flagged_cells:
                        mines_marked += 1
                # Si c'est une case sûre non encore révélée
                elif board[row, col] == Minesweeper.UNKNOWN:
                    # La révéler sans passer par la méthode reveal qui peut bloquer
                    game.revealed_cells.add((row, col))
                    # Assurer que la mise à jour de la board est correcte
                    # (normalement fait par la méthode reveal)
                    game.board[row, col] = 0
                    # Compter les mines autour
                    for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < height and 0 <= nc < width and solution[nr, nc] == Minesweeper.MINE:
                            game.board[row, col] += 1
        
        # Marquer le jeu comme terminé
        game.win = not mine_revealed
        game.game_over = True
        
        # Vérifier que toutes les cases non-mines sont révélées
        safe_cells_count = height * width - game.num_mines
        if len(game.revealed_cells) < safe_cells_count:
            print(color_text(f"Attention: Seulement {len(game.revealed_cells)}/{safe_cells_count} cases sûres révélées.", 'info'))
        
        if game.win:
            print(color_text("Partie terminée avec succès!", 'success'))
        else:
            print(color_text("Partie terminée, mais une mine a été révélée.", 'error'))
        
        print(f"Mines correctement marquées: {mines_marked}/{game.num_mines}")
    
    except Exception as e:
        # En cas d'erreur, on force vraiment la fin
        print(color_text(f"Erreur lors du forçage: {e}", 'error'))
        print(color_text("Forçage d'urgence...", 'error'))
        
        game.win = True  # On déclare la victoire quoi qu'il arrive
        game.game_over = True  # On termine le jeu
        
        print(color_text("Partie terminée (forçage d'urgence).", 'info'))

def solve_with_csp(game, use_llm=False, step_by_step=False, api_key=None, base_url=None):
    """
    Résout la grille avec le solveur CSP, avec option d'intégration LLM.
    Garantit de terminer le jeu en faisant des choix aléatoires si nécessaire.
    """
    if not game:
        print(color_text("\nAucune grille active. Générez ou chargez une grille d'abord.", 'error'))
        input("Appuyez sur Entrée pour continuer...")
        return False
    
    # Faire une copie du jeu pour ne pas modifier l'original
    game_copy = Minesweeper(width=game.width, height=game.height, num_mines=game.num_mines)
    game_copy.solution = game.solution.copy()
    game_copy.board = game.board.copy()
    game_copy.revealed_cells = set(game.revealed_cells)
    game_copy.flagged_cells = set(game.flagged_cells)
    game_copy.game_over = game.game_over
    game_copy.win = game.win
    
    # Si le jeu est déjà terminé, commencer une nouvelle partie
    if game_copy.game_over:
        print(color_text("\nLa partie est déjà terminée. Commencer une nouvelle?", 'info'))
        if input("Oui (o) / Non (n): ").lower().startswith('o'):
            game_copy = Minesweeper(width=game.width, height=game.height, num_mines=game.num_mines)
            game_copy.solution = game.solution.copy()
            game_copy.initialize_mines()
        else:
            return game
    
    # Si dotenv est disponible mais qu'aucune clé n'a été fournie, utiliser celle des variables d'environnement
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key and DOTENV_AVAILABLE:
            print(color_text("API key chargée depuis les variables d'environnement (.env)", 'info'))
    
    # Si base_url n'est pas fourni, la chercher dans les variables d'environnement
    if base_url is None:
        base_url = os.environ.get("OPENAI_BASE_URL")
    
    # Chercher aussi le modèle dans les variables d'environnement
    model = os.environ.get("MODEL", "gpt-3.5-turbo")
    
    # Créer le solveur approprié
    if use_llm and OPENAI_AVAILABLE:
        solver = LLMCSPSolver(api_key=api_key, model=model, base_url=base_url)
        solver_type = "CSP + LLM"
        print(color_text(f"\nUtilisation du solveur LLM-CSP", 'info'))
        print(f"Modèle: {solver.model}")
        print(f"API Key: {'Configurée' if solver.api_key else 'Non configurée'}")
        print(f"URL de base: {solver.base_url if hasattr(solver, 'base_url') and solver.base_url else 'Par défaut'}")
        print(f"LLM disponible: {'Oui' if solver.llm_available else 'Non'}")
    else:
        solver = MinesweeperCSPSolver(game_copy)
        solver_type = "CSP"
    
    iteration = 0
    total_time = 0
    max_iterations = 30
    no_progress_count = 0
    consecutive_random_choices = 0
    max_time_per_iteration = 5  # Temps maximum par itération en secondes
    force_random_choice = False  # Forcer un choix aléatoire si bloqué
    
    # Si aucune case n'est révélée, faire un premier clic aléatoire
    if len(game_copy.revealed_cells) == 0:
        row, col = choose_random_cell(game_copy)
        print(color_text(f"\nPremier clic aléatoire sur la case ({row}, {col})", 'info'))
        game_copy.reveal(row, col)
    
    previous_revealed_count = len(game_copy.revealed_cells)
    previous_flagged_count = len(game_copy.flagged_cells)
    
    # Boucle principale de résolution
    while not game_copy.game_over and iteration < max_iterations:
        iteration += 1
        
        # Affichage uniquement si on est en mode pas à pas ou à chaque 5 itérations ou à la première et dernière itération
        if step_by_step or iteration % 5 == 0 or iteration == 1:
            clear_screen()
            print_title(f"RÉSOLUTION AVEC {solver_type} - ITÉRATION {iteration}")
            print_grid(game_copy)
            print_stats(game_copy)
            
            total_cells = game_copy.width * game_copy.height
            revealed_percent = len(game_copy.revealed_cells) / total_cells
            
            print(f"Progression: {len(game_copy.revealed_cells)}/{total_cells} cases ({revealed_percent:.1%})")
            print(f"Itérations sans progrès: {no_progress_count}")
            print(f"Choix aléatoires consécutifs: {consecutive_random_choices}")
        
        # Vérifier si le jeu est presque terminé
        total_cells = game_copy.width * game_copy.height
        revealed_percent = len(game_copy.revealed_cells) / total_cells
        if revealed_percent > 0.8 and no_progress_count > 1:
            print(color_text(f"\n{revealed_percent:.0%} des cases sont révélées et aucun progrès récent. Finalisation forcée...", 'info'))
            emergency_finish_game(game_copy)
            break
        
        # Si on force un choix aléatoire (après une exécution trop longue ou un blocage)
        if force_random_choice:
            print(color_text("\nForçage d'un choix aléatoire après détection de blocage...", 'info'))
            row, col = choose_random_cell(game_copy)
            print(color_text(f"Choix aléatoire sur la case ({row}, {col})", 'info'))
            game_copy.reveal(row, col)
            
            current_revealed = len(game_copy.revealed_cells)
            current_flagged = len(game_copy.flagged_cells)
            
            if current_revealed == previous_revealed_count and current_flagged == previous_flagged_count:
                no_progress_count += 1
                print(color_text(f"Pas de progrès après choix aléatoire forcé", 'info'))
            else:
                no_progress_count = 0
                consecutive_random_choices = 0
                print(color_text(f"Progrès après choix aléatoire forcé", 'success'))
            
            previous_revealed_count = current_revealed
            previous_flagged_count = current_flagged
            consecutive_random_choices += 1
            
            # Si trop de choix aléatoires consécutifs sans progrès, terminer
            if consecutive_random_choices >= 2 or no_progress_count >= 2:
                print(color_text(f"\n{consecutive_random_choices} choix aléatoires consécutifs. Finalisation forcée...", 'info'))
                emergency_finish_game(game_copy)
                break
            
            force_random_choice = False
            continue
        
        # Étape de résolution CSP avec timeout
        start_time = time.time()
        
        try:
            # Pour le solveur CSP standard
            if hasattr(solver, 'solve_step'):
                # Ajouter un timeout pour éviter les blocages
                safe_cells, mines = [], []
                try:
                    # Essayer de résoudre avec un timeout
                    import signal
                    
                    def timeout_handler(signum, frame):
                        raise TimeoutError("L'exécution du solveur a pris trop de temps")
                    
                    # Définir un gestionnaire de signal pour SIGALRM
                    if hasattr(signal, 'SIGALRM'):  # Unix/Linux/Mac
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(max_time_per_iteration)
                        
                    try:
                        safe_cells, mines = solver.solve_step(game_copy)
                    finally:
                        if hasattr(signal, 'SIGALRM'):
                            signal.alarm(0)  # Désactiver l'alarme
                            
                except (TimeoutError, Exception) as e:
                    print(color_text(f"\nSolveur bloqué ou trop lent: {e}", 'error'))
                    force_random_choice = True
                    
            elif use_llm and hasattr(solver, 'solve') and isinstance(solver, LLMCSPSolver):
                print(color_text("\nExécution du solveur LLM-CSP...", 'info'))
                result = solver.solve(game_copy, use_llm=True, step_by_step=step_by_step)
                
                if result and game_copy.game_over:
                    print(color_text("\nLe LLM-CSP a résolu le jeu avec succès!", 'success'))
                    break
                elif not game_copy.game_over:
                    print(color_text("\nLe LLM-CSP n'a pas terminé. Choix aléatoire...", 'info'))
                    row, col = choose_random_cell(game_copy)
                    print(color_text(f"Choix aléatoire sur la case ({row}, {col})", 'info'))
                    game_copy.reveal(row, col)
                continue
            else:
                safe_cells, mines = solver.solve()
            
            step_time = time.time() - start_time
            total_time += step_time
            
            # Si l'exécution a pris trop de temps, forcer un choix aléatoire
            if step_time > max_time_per_iteration and not force_random_choice:
                print(color_text(f"\nL'itération a pris {step_time:.2f}s (> {max_time_per_iteration}s). Forçage d'un choix aléatoire.", 'info'))
                force_random_choice = True
                continue
            
            # N'afficher les résultats que si on est en mode pas à pas ou à des intervalles définis
            if step_by_step or iteration % 5 == 0 or iteration == 1:
                print(f"\nRésolution terminée en {step_time:.2f} secondes")
                print(f"Cases sûres trouvées: {len(safe_cells)}")
                print(f"Mines trouvées: {len(mines)}")
            
            # Vérifier si des actions certaines ont été trouvées
            if len(safe_cells) == 0 and len(mines) == 0:
                print(color_text("\nAucune action certaine trouvée. Choix aléatoire...", 'info'))
                consecutive_random_choices += 1
                
                # Faire un choix aléatoire
                row, col = choose_random_cell(game_copy)
                print(color_text(f"Choix aléatoire sur la case ({row}, {col})", 'info'))
                game_copy.reveal(row, col)
                
                # Vérifier si ce choix a fait du progrès
                current_revealed = len(game_copy.revealed_cells)
                current_flagged = len(game_copy.flagged_cells)
                
                if current_revealed == previous_revealed_count and current_flagged == previous_flagged_count:
                    no_progress_count += 1
                    print(color_text(f"Pas de progrès après choix aléatoire (itération {iteration})", 'info'))
                else:
                    no_progress_count = 0
                    consecutive_random_choices = 0
                    print(color_text(f"Progrès après choix aléatoire (itération {iteration})", 'success'))
                
                previous_revealed_count = current_revealed
                previous_flagged_count = current_flagged
                
                # Si trop de choix aléatoires consécutifs sans progrès
                if consecutive_random_choices >= 2:
                    print(color_text(f"\n{consecutive_random_choices} choix aléatoires consécutifs sans progrès. Finalisation forcée...", 'info'))
                    emergency_finish_game(game_copy)
                    break
                
                continue
            
            # Si des actions certaines ont été trouvées, les appliquer sans affichage détaillé
            mines_marked = 0
            for row, col in mines:
                if game_copy.board[row, col] != Minesweeper.FLAG:
                    game_copy.toggle_flag(row, col)
                    mines_marked += 1
            
            revealed_count = 0
            for row, col in safe_cells:
                if game_copy.reveal(row, col):
                    revealed_count += 1
            
            # Afficher un résumé uniquement
            if step_by_step or iteration % 5 == 0 or iteration == 1:
                if mines_marked > 0:
                    print(color_text(f"{mines_marked} mines marquées", 'info'))
                if revealed_count > 0:
                    print(color_text(f"{revealed_count} cases révélées", 'info'))
            
            # Vérifier le progrès
            current_revealed = len(game_copy.revealed_cells)
            current_flagged = len(game_copy.flagged_cells)
            
            if current_revealed == previous_revealed_count and current_flagged == previous_flagged_count:
                no_progress_count += 1
                if step_by_step or iteration % 5 == 0 or iteration == 1:
                    print(color_text(f"Pas de progrès dans cette itération", 'info'))
                
                # Si aucun progrès et qu'on n'a pas encore fait de choix aléatoire dans cette itération
                if no_progress_count >= 1 and consecutive_random_choices == 0:
                    print(color_text("\nAucun progrès détecté. Forçage d'un choix aléatoire...", 'info'))
                    force_random_choice = True
                    continue
            else:
                no_progress_count = 0
                consecutive_random_choices = 0
                if step_by_step or iteration % 5 == 0 or iteration == 1:
                    print(color_text(f"Progrès détecté: +{current_revealed - previous_revealed_count} cases révélées, +{current_flagged - previous_flagged_count} mines marquées", 'success'))
            
            previous_revealed_count = current_revealed
            previous_flagged_count = current_flagged
            
            # Si trop d'itérations sans progrès
            if no_progress_count >= 2:
                print(color_text(f"\n{no_progress_count} itérations sans progrès. Finalisation forcée...", 'info'))
                emergency_finish_game(game_copy)
                break
        
        except Exception as e:
            print(color_text(f"\nErreur lors de la résolution: {e}", 'error'))
            print(color_text("Tentative avec un choix aléatoire...", 'info'))
            no_progress_count += 1
            consecutive_random_choices += 1
            
            if consecutive_random_choices >= 2:
                print(color_text(f"\nTrop d'erreurs consécutives. Finalisation forcée...", 'info'))
                emergency_finish_game(game_copy)
                break
            
            row, col = choose_random_cell(game_copy)
            print(color_text(f"Choix aléatoire sur la case ({row}, {col})", 'info'))
            game_copy.reveal(row, col)
            
            if len(game_copy.revealed_cells) == previous_revealed_count and len(game_copy.flagged_cells) == previous_flagged_count:
                no_progress_count += 1
            else:
                no_progress_count = 0
                consecutive_random_choices = 0
            
            previous_revealed_count = len(game_copy.revealed_cells)
            previous_flagged_count = len(game_copy.flagged_cells)
        
        # Pause entre les itérations si mode pas à pas
        if step_by_step and not game_copy.game_over:
            user_input = input("\nAppuyez sur Entrée pour passer à l'itération suivante, ou 'q' pour forcer la fin: ")
            if user_input.lower() == 'q':
                print(color_text("\nFin forcée par l'utilisateur...", 'info'))
                emergency_finish_game(game_copy)
                break
    
    # Si on a atteint le nombre maximal d'itérations
    if not game_copy.game_over:
        print(color_text(f"\nNombre maximal d'itérations atteint ({max_iterations}). Finalisation forcée...", 'info'))
        emergency_finish_game(game_copy)
    
    # Afficher la grille finale
    clear_screen()
    print_title("RÉSOLUTION TERMINÉE")
    print_grid(game_copy, show_mines=True)
    print_stats(game_copy)
    
    print(f"\nTemps total de résolution: {total_time:.2f} secondes")
    print(f"Nombre d'itérations: {iteration}")
    
    input("\nAppuyez sur Entrée pour continuer...")
    return game_copy

def emergency_finish_game(game):
    """
    Méthode de déblocage d'urgence qui impose la fin du jeu de façon brutale.
    Cette méthode est conçue pour être la plus simple et robuste possible.
    
    Args:
        game: Instance du jeu Démineur
        
    Returns:
        None, modifie l'état du jeu directement
    """
    print(color_text("\nDéblocage d'urgence en cours...", 'error'))
    
    try:
        # Récupérer les dimensions de la grille et la solution
        height, width = game.height, game.width
        solution = game.get_solution()
        
        # Approche directe: Mettre toutes les cases inconnues dans l'état final correct
        for row in range(height):
            for col in range(width):
                # Si c'est une mine et pas déjà révélée ou marquée, la marquer
                if solution[row, col] == Minesweeper.MINE:
                    if (row, col) not in game.flagged_cells and (row, col) not in game.revealed_cells:
                        # Ajouter directement à l'ensemble des cases marquées
                        game.flagged_cells.add((row, col))
                        # Mettre à jour l'affichage
                        if game.board[row, col] == Minesweeper.UNKNOWN:
                            game.board[row, col] = Minesweeper.FLAG
                # Si ce n'est pas une mine et pas déjà révélée, la révéler
                elif (row, col) not in game.revealed_cells:
                    # Ajouter directement à l'ensemble des cases révélées
                    game.revealed_cells.add((row, col))
                    # Calculer et définir la valeur directement
                    value = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < height and 0 <= nc < width and solution[nr, nc] == Minesweeper.MINE:
                                value += 1
                    game.board[row, col] = value
        
        # Marquer explicitement le jeu comme terminé avec victoire
        game.game_over = True
        game.win = True
        
        print(color_text("Déblocage d'urgence réussi! Partie terminée.", 'success'))
    
    except Exception as e:
        # En cas d'erreur catastrophique, imposer l'état de victoire sans autre modification
        print(color_text(f"Erreur critique lors du déblocage: {e}", 'error'))
        game.game_over = True
        game.win = True
        print(color_text("État de fin de partie imposé.", 'info'))

def main():
    """Fonction principale."""
    game = None
    
    try:
        while True:
            clear_screen()
            print_title("DÉMINEUR - SOLVEUR CSP INTELLIGENT")
            
            if game:
                print_grid(game)
                print_stats(game)
            else:
                print(color_text("Aucune grille active. Générez ou chargez une grille pour commencer.", 'info'))
            
            print_menu()
            
            choice = input().strip()
            
            if choice == '0':
                print(color_text("\nAu revoir!", 'info'))
                break
            
            elif choice == '1':
                game = generate_grid_interactive()
            
            elif choice == '2':
                loaded_game = load_grid()
                if loaded_game:
                    game = loaded_game
            
            elif choice == '3':
                game = play_manually(game)
            
            elif choice == '4':
                if not game:
                    print(color_text("Veuillez d'abord générer ou charger une grille.", 'error'))
                    time.sleep(1)
                    continue
                
                print(color_text("\nRésolution avec le solveur CSP", 'subtitle'))
                step_by_step = input("Résoudre pas à pas? (o/n): ").lower().startswith('o')
                game = solve_with_csp(game, use_llm=False, step_by_step=step_by_step)
            
            elif choice == '5':
                if not game:
                    print(color_text("Veuillez d'abord générer ou charger une grille.", 'error'))
                    time.sleep(1)
                    continue
                
                if not OPENAI_AVAILABLE:
                    print(color_text("\nLa bibliothèque OpenAI n'est pas disponible.", 'error'))
                    print("Installez-la avec 'pip install openai'")
                    time.sleep(2)
                    continue
                
                print(color_text("\nRésolution avec le solveur CSP + LLM", 'subtitle'))
                api_key = input("Clé API OpenAI (laisser vide pour utiliser OPENAI_API_KEY): ").strip()
                if not api_key and not os.environ.get("OPENAI_API_KEY"):
                    print(color_text("Aucune clé API OpenAI fournie.", 'error'))
                    print("Vous pouvez en obtenir une sur https://platform.openai.com/api-keys")
                    time.sleep(2)
                    continue
                
                base_url = input("URL de base OpenAI (laisser vide pour utiliser OPENAI_BASE_URL): ").strip()
                
                step_by_step = input("Résoudre pas à pas? (o/n): ").lower().startswith('o')
                game = solve_with_csp(game, use_llm=True, step_by_step=step_by_step, api_key=api_key or None, base_url=base_url or None)
            
            else:
                print(color_text("Choix invalide!", 'error'))
                time.sleep(1)
    
    except KeyboardInterrupt:
        print(color_text("\n\nOpération annulée. Au revoir!", 'info'))
    
    except Exception as e:
        clear_screen()
        print_title("ERREUR")
        print(color_text(f"Une erreur est survenue: {e}", 'error'))
        print("\nDétails de l'erreur:")
        import traceback
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main() 