# Résolution automatique du Démineur par contraintes

Ce projet implémente un solveur automatique pour le jeu du Démineur en utilisant la programmation par contraintes (CSP - Constraint Satisfaction Problem) et peut également utiliser un modèle de langage (LLM) pour résoudre des situations ambiguës.

## Description

Le Démineur est modélisé comme un problème de satisfaction de contraintes où :
- Chaque case inconnue est représentée par une variable booléenne (présence ou non d'une mine)
- Chaque case découverte avec un chiffre impose une contrainte sur son voisinage
- L'objectif est de déterminer avec certitude les cases contenant des mines et celles qui sont sûres

## Structure du projet

- `simple_csp_cli.py` : Interface en ligne de commande avec affichage coloré
- `minesweeper.py` : Implémentation du jeu du Démineur
- `csp_solver.py` : Solveur basé sur la programmation par contraintes
- `llm_csp_solver.py` : Solveur combinant CSP et LLM pour les situations complexes
- `generate_grid.py` : Script de génération de grilles simples
- `generate_minesweeper.py` : Générateur avancé de grilles de démineur
- `requirements.txt` : Dépendances du projet

## Installation

```bash
# Créer et activer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate  # Sous Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### Interface en ligne de commande (recommandée)

```bash
python simple_csp_cli.py
```

L'interface en ligne de commande permet de :
- Générer des grilles aléatoires avec des paramètres personnalisés
- Charger des grilles depuis des fichiers texte
- Jouer manuellement avec une interface textuelle colorée
- Résoudre les grilles avec le solveur CSP
- Résoudre les grilles avec le solveur CSP + LLM (nécessite une clé API OpenAI)

### Génération de grilles

```bash
# Générer une grille avec paramètres par défaut
python generate_minesweeper.py

# Personnaliser les paramètres
python generate_minesweeper.py --width 10 --height 10 --mines 15 --reveal 0.3

# Afficher la grille générée
python generate_minesweeper.py --display
```

Options disponibles :
- `--width WIDTH` : Largeur de la grille (défaut: 9)
- `--height HEIGHT` : Hauteur de la grille (défaut: 9)
- `--mines MINES` : Nombre de mines (défaut: 10)
- `--reveal REVEAL` : Pourcentage de cases non-mines à révéler (0.0-1.0) (défaut: 0.3)
- `--seed SEED` : Graine aléatoire pour la reproductibilité
- `--output OUTPUT` : Fichier de sortie (défaut: grid.txt)
- `--display` : Afficher la grille générée

### Utilisation en code Python

```python
from minesweeper import Minesweeper
from csp_solver import MinesweeperCSPSolver

# Créer une instance du jeu
game = Minesweeper(width=9, height=9, num_mines=10)
game.initialize_mines()

# Initialiser le jeu avec quelques clics
game.reveal(4, 4)  # Premier clic au centre

# Afficher la grille
game.display()

# Utiliser le solveur CSP
solver = MinesweeperCSPSolver(game)
safe_cells, mine_cells = solver.solve()

print(f"Cellules sûres: {safe_cells}")
print(f"Mines identifiées: {mine_cells}")

# Mettre à jour le jeu avec les résultats
solver.update_game(auto_play=True)

# Afficher la grille mise à jour
game.display()
```

## Stratégies de résolution

Le projet propose deux stratégies de résolution :

1. **CSP** : Utilise la programmation par contraintes pure pour résoudre le problème
   - Basée sur la bibliothèque `python-constraint`
   - Identifie les cases sûres et les mines avec une certitude de 100%
   - Peut être bloquée dans des situations ambiguës

2. **CSP + LLM** : Combine la programmation par contraintes avec un LLM pour gérer les situations ambiguës
   - Utilise un modèle OpenAI pour analyser les situations complexes
   - Implémente un raisonnement avancé lorsque la programmation par contraintes seule est insuffisante
   - Peut proposer des actions avec différents niveaux de confiance
   - Maintient un historique des décisions pour du debugging

## Configuration OpenAI

Pour utiliser le solveur CSP + LLM, vous devez configurer votre clé API OpenAI de l'une des façons suivantes :
1. Définir la variable d'environnement `OPENAI_API_KEY`
2. La fournir directement au constructeur `LLMCSPSolver(api_key="votre-clé-api")`
3. La fournir lors de l'utilisation de l'interface en ligne de commande

## Dépendances

- `numpy` : Gestion des tableaux et calculs numériques
- `matplotlib` : Visualisation optionnelle des grilles
- `python-constraint` : Résolution du problème CSP
- `openai` : Communication avec les modèles OpenAI (optionnel)

## Références

- A Constraint-Based Approach to Solving Minesweeper (Bayer et Snyder, 2013)
- Minesweeper is NP-complete (Princeton, 2013) 