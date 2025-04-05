#!/usr/bin/env python3
"""
Module d'intégration entre un LLM (OpenAI) et notre solveur CSP pour le démineur.
Ce module permet d'utiliser un LLM pour assister dans la résolution de situations
complexes ou ambiguës dans le jeu du démineur.
"""

import os
import json
import time
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Set
from minesweeper import Minesweeper
from csp_solver import MinesweeperCSPSolver

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("python-dotenv library not available. Install with 'pip install python-dotenv' for .env file support")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI library not available. Please install it with 'pip install openai'")

class LLMCSPSolver:
    """
    Classe qui combine un LLM et un solveur CSP pour résoudre le démineur.
    """
    
    # Système prompt pour définir le contexte du LLM
    SYSTEM_PROMPT = """
    Tu es un expert en démineur et en résolution de problèmes de contraintes.
    Ta tâche est d'analyser des situations dans une grille de démineur et de proposer la meilleure action à prendre.
    Utilise ton raisonnement et ta connaissance des règles du démineur pour suggérer soit:
    1. Une case sûre à révéler
    2. Une case qui contient très probablement une mine
    3. Une stratégie de résolution que le solveur CSP pourrait appliquer

    Voici les règles fondamentales du démineur que tu dois appliquer:
    - Chaque chiffre indique le nombre de mines adjacentes (horizontal, vertical, diagonal)
    - Il faut éviter de cliquer sur une mine
    - Le but est de révéler toutes les cases sans mine
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", base_url: Optional[str] = None):
        """
        Initialise le solveur LLM-CSP.
        
        Args:
            api_key: Clé API OpenAI (si None, cherche dans les variables d'environnement ou .env)
            model: Modèle OpenAI à utiliser
            base_url: URL de base pour l'API OpenAI (si None, cherche dans les variables d'environnement)
        """
        # Charger les variables d'environnement depuis .env si disponible
        if DOTENV_AVAILABLE:
            load_dotenv()  # Charge les variables depuis .env par défaut
        
        self.model = model
        # Priorité: paramètre api_key > variable d'environnement
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        
        # Vérifier si OpenAI est disponible et si une clé API est fournie
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            self.llm_available = True
        else:
            self.llm_available = False
            
        # Conservation de l'historique des décisions
        self.decision_history = []
        
    def format_grid_for_llm(self, game: Minesweeper) -> str:
        """
        Formate la grille du démineur pour l'envoi au LLM.
        
        Args:
            game: Instance du jeu Démineur
            
        Returns:
            Représentation textuelle de la grille
        """
        board = game.get_visible_board()
        width = game.width
        height = game.height
        
        grid_repr = "État actuel de la grille:\n"
        
        # Ajouter les indices de colonnes
        grid_repr += "   "
        for col in range(width):
            grid_repr += f"{col} "
        grid_repr += "\n"
        
        # Ajouter une ligne de séparation
        grid_repr += "  +"
        for _ in range(width):
            grid_repr += "--"
        grid_repr += "\n"
        
        # Ajouter le contenu de la grille
        for row in range(height):
            grid_repr += f"{row} |"
            for col in range(width):
                cell_value = board[row, col]
                
                if cell_value == Minesweeper.UNKNOWN:
                    grid_repr += "? "
                elif cell_value == Minesweeper.FLAG:
                    grid_repr += "F "
                elif cell_value == 0:
                    grid_repr += "  "
                else:
                    grid_repr += f"{cell_value} "
            
            grid_repr += "\n"
        
        # Ajouter des informations supplémentaires
        grid_repr += f"\nNombre total de mines: {game.num_mines}\n"
        grid_repr += f"Nombre de drapeaux placés: {len(game.flagged_cells)}\n"
        grid_repr += f"Nombre de cases non révélées: {game.get_unrevealed_count()}\n"
        
        return grid_repr
    
    def consult_llm(self, game: Minesweeper, reasoning_context: str) -> Dict[str, Any]:
        """
        Consulte le LLM pour obtenir des insights sur la situation actuelle.
        
        Args:
            game: Instance du jeu Démineur
            reasoning_context: Contexte supplémentaire pour le LLM
            
        Returns:
            Réponse structurée du LLM
        """
        if not self.llm_available:
            return {"error": "LLM not available"}
        
        grid_repr = self.format_grid_for_llm(game)
        
        prompt = f"""
        {grid_repr}
        
        {reasoning_context}
        
        Analyse la situation et propose une action. Format de réponse:

        ```json
        {{
            "reasoning": "ton raisonnement détaillé ici",
            "action_type": "reveal_safe | flag_mine | random | strategy",
            "coordinates": [row, col],  // si applicable
            "confidence": 0.0 à 1.0,    // ton niveau de confiance
            "strategy": "description de la stratégie si action_type est strategy"
        }}
        ```
        
        Réponds UNIQUEMENT avec le JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Extraire le JSON de la réponse
            content = response.choices[0].message.content
            # Nettoyer la réponse si nécessaire (enlever les ``` et json)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            # Parser le JSON
            result = json.loads(content.strip())
            return result
            
        except Exception as e:
            print(f"Erreur lors de la consultation du LLM: {e}")
            return {
                "error": str(e),
                "action_type": "random",
                "confidence": 0.0
            }
    
    def choose_random_cell(self, game: Minesweeper) -> Tuple[int, int]:
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
            return unrevealed[np.random.randint(0, len(unrevealed))]
        else:
            # Cas d'erreur (ne devrait pas arriver)
            return (0, 0)
    
    def solve(self, game: Minesweeper, use_llm: bool = True, step_by_step: bool = False) -> bool:
        """
        Résout le jeu de démineur en combinant le solveur CSP et le LLM.
        
        Args:
            game: Instance du jeu Démineur
            use_llm: Si True, utilise le LLM pour assister la résolution
            step_by_step: Si True, effectue la résolution pas à pas
            
        Returns:
            True si le jeu a été résolu, False sinon
        """
        iteration = 0
        total_time = 0
        
        # Variables pour gérer les situations de blocage
        no_progress_count = 0
        consecutive_random_choices = 0
        previous_revealed_count = len(game.revealed_cells)
        previous_flagged_count = len(game.flagged_cells)
        max_iterations = 30
        
        # Initialiser le solveur CSP avec le jeu actuel
        csp_solver = MinesweeperCSPSolver(game)
        
        # Si le jeu n'a pas de mines, révéler une case aléatoire pour commencer
        if len(game.revealed_cells) == 0:
            row, col = self.choose_random_cell(game)
            print(f"Premier clic sur la case ({row}, {col})")
            game.reveal(row, col)
        
        while not game.game_over and iteration < max_iterations:
            iteration += 1
            print(f"\nItération {iteration}")
            
            # Vérifier si le jeu est presque terminé (> 80% des cases sont révélées)
            revealed_percent = len(game.revealed_cells) / (game.width * game.height)
            if revealed_percent > 0.8 and no_progress_count > 1:
                print(f"\n{revealed_percent:.0%} des cases sont révélées et aucun progrès récent.")
                print("Finalisation forcée...")
                return False
            
            # Si on a fait 2 choix aléatoires consécutifs sans progrès, terminer
            if consecutive_random_choices >= 2:
                print(f"\n{consecutive_random_choices} choix aléatoires consécutifs sans progrès.")
                print("Finalisation forcée...")
                return False
            
            # 1. Essayer d'abord le solveur CSP
            start_time = time.time()
            safe_cells, mines = csp_solver.solve_step(game)
            step_time = time.time() - start_time
            total_time += step_time
            
            print(f"Résolution CSP terminée en {step_time:.2f} secondes")
            print(f"Cases sûres trouvées: {len(safe_cells)}")
            print(f"Mines trouvées: {len(mines)}")
            
            # Mettre à jour la grille avec les résultats du solveur CSP
            mines_marked = 0
            for row, col in mines:
                if game.board[row, col] != Minesweeper.FLAG:
                    game.toggle_flag(row, col)
                    mines_marked += 1
            
            revealed_count = 0
            for row, col in safe_cells:
                if game.reveal(row, col):
                    revealed_count += 1
            
            # Vérifier s'il y a eu du progrès dans cette itération
            current_revealed = len(game.revealed_cells)
            current_flagged = len(game.flagged_cells)
            
            if revealed_count == 0 and mines_marked == 0:
                no_progress_count += 1
                print(f"\nAucune action effectuée. Itérations sans progrès: {no_progress_count}")
                
                # Si au moins 2 itérations sans progrès, faire un choix aléatoire immédiatement
                if no_progress_count >= 2:
                    # Vérifier si le jeu est terminé
                    if game.game_over:
                        break
                    
                    print(f"\n{no_progress_count} itérations sans progrès. Choix aléatoire immédiat...")
                    consecutive_random_choices += 1
                    
                    if use_llm and self.llm_available:
                        # Consultation du LLM pour obtenir un conseil
                        reasoning_context = f"""
                        Le solveur CSP n'a pas pu déterminer d'action certaine.
                        Analyse la grille et propose une action basée sur des probabilités ou des stratégies avancées.
                        Itération actuelle: {iteration}
                        Nombre d'itérations sans progrès: {no_progress_count}
                        """
                        
                        llm_response = self.consult_llm(game, reasoning_context)
                        self.decision_history.append(llm_response)
                        
                        if "error" in llm_response:
                            print(f"Erreur LLM: {llm_response['error']}")
                            action_type = "random"
                        else:
                            print(f"Raisonnement LLM: {llm_response.get('reasoning', 'Non fourni')}")
                            action_type = llm_response.get("action_type", "random")
                        
                        if action_type == "reveal_safe" and "coordinates" in llm_response:
                            row, col = llm_response["coordinates"]
                            confidence = llm_response.get("confidence", 0.0)
                            print(f"Le LLM suggère de révéler la case ({row}, {col}) avec une confiance de {confidence:.2f}")
                            game.reveal(row, col)
                        
                        elif action_type == "flag_mine" and "coordinates" in llm_response:
                            row, col = llm_response["coordinates"]
                            confidence = llm_response.get("confidence", 0.0)
                            print(f"Le LLM suggère de marquer la case ({row}, {col}) comme mine avec une confiance de {confidence:.2f}")
                            game.toggle_flag(row, col)
                        
                        else:  # random ou autre
                            row, col = self.choose_random_cell(game)
                            print(f"Choix aléatoire: révéler la case ({row}, {col})")
                            game.reveal(row, col)
                    else:
                        # Choisir une case aléatoire
                        row, col = self.choose_random_cell(game)
                        print(f"Choix aléatoire: révéler la case ({row}, {col})")
                        game.reveal(row, col)
                    
                    # Vérifier si ce choix aléatoire a fait du progrès
                    new_revealed_count = len(game.revealed_cells)
                    if new_revealed_count > current_revealed:
                        no_progress_count = 0
                        consecutive_random_choices = 0
                        print(f"Progrès réalisé après choix aléatoire! +{new_revealed_count - current_revealed} cases révélées")
                    else:
                        print("Aucun progrès après le choix aléatoire.")
            else:
                progress_message = f"Progrès: +{revealed_count} cases révélées, +{mines_marked} mines marquées"
                print(progress_message)
                no_progress_count = 0
                consecutive_random_choices = 0
            
            previous_revealed_count = len(game.revealed_cells)
            previous_flagged_count = len(game.flagged_cells)
            
            # Vérifier si le jeu est terminé
            if game.game_over:
                break
            
            # Pause entre les itérations si mode pas à pas
            if step_by_step and not game.game_over:
                input("Appuyez sur Entrée pour continuer...")
        
        # Afficher le résultat final
        print("\nRésultat final:")
        print(f"Total du temps de résolution: {total_time:.2f} secondes")
        print(f"Nombre d'itérations: {iteration}")
        
        if game.win:
            print("Victoire! Toutes les mines ont été correctement identifiées.")
            return True
        else:
            print("Défaite! Une mine a été révélée ou le jeu a été interrompu.")
            return False
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """
        Retourne l'historique des décisions du LLM.
        
        Returns:
            Liste des décisions prises par le LLM
        """
        return self.decision_history


def main():
    """Fonction de test pour le solveur LLM-CSP."""
    from generate_grid import load_grid_from_file
    import argparse
    
    parser = argparse.ArgumentParser(description='Solveur de démineur utilisant CSP et LLM')
    parser.add_argument('--load', type=str, help='Charger une grille depuis un fichier')
    parser.add_argument('--width', type=int, default=9, help='Largeur de la grille')
    parser.add_argument('--height', type=int, default=9, help='Hauteur de la grille')
    parser.add_argument('--mines', type=int, default=10, help='Nombre de mines')
    parser.add_argument('--no-llm', action='store_true', help='Désactiver l\'utilisation du LLM')
    parser.add_argument('--step', action='store_true', help='Exécution pas à pas')
    parser.add_argument('--api-key', type=str, help='Clé API OpenAI (sinon utilise OPENAI_API_KEY)')
    parser.add_argument('--base-url', type=str, help='URL de base pour l\'API OpenAI (sinon utilise OPENAI_BASE_URL)')
    args = parser.parse_args()
    
    # Créer ou charger une grille
    if args.load:
        game = load_grid_from_file(args.load)
        if game is None:
            print(f"Erreur: Impossible de charger la grille depuis {args.load}")
            return
        print(f"Grille chargée depuis {args.load}")
    else:
        game = Minesweeper(width=args.width, height=args.height, num_mines=args.mines)
        game.initialize_mines()
        print(f"Nouvelle grille générée: {args.width}x{args.height}, {args.mines} mines")
    
    # Créer le solveur
    solver = LLMCSPSolver(api_key=args.api_key, base_url=args.base_url)
    
    # Résoudre la grille
    solver.solve(game, use_llm=not args.no_llm, step_by_step=args.step)


if __name__ == "__main__":
    main() 