# Résolution automatique du Démineur par contraintes

Ce projet implémente un solveur automatique pour le jeu du Démineur en utilisant la programmation par contraintes (CSP - Constraint Satisfaction Problem) et peut également utiliser un modèle de langage (LLM) pour résoudre des situations ambiguës.

## Description

Le Démineur est modélisé comme un problème de satisfaction de contraintes où :
- Chaque case inconnue est représentée par une variable booléenne (présence ou non d'une mine)
- Chaque case découverte avec un chiffre impose une contrainte sur son voisinage
- L'objectif est de déterminer avec certitude les cases contenant des mines et celles qui sont sûres

## Structure du projet

- `test.py` : Interface graphique principale avec PyQt6
- `simple_csp_cli.py` : Interface en ligne de commande avec affichage coloré
- `minesweeper.py` : Implémentation du jeu du Démineur
- `csp_solver.py` : Solveur basé sur la programmation par contraintes
- `llm_csp_solver.py` : Solveur combinant CSP et LLM pour les situations complexes
- `llm_grid_generator.py` : Générateur de grilles utilisant un LLM pour créer des puzzles intéressants
- `generate_grid.py` : Script de génération de grilles simples
- `generate_minesweeper.py` : Générateur avancé de grilles de démineur
- `projet_minesweeper.ipynb` : Notebook Jupyter détaillant le projet
- `create_notebook.py` : Script de génération du notebook
- `requirements.txt` : Dépendances du projet
- `.env.example` : Exemple de fichier de configuration des variables d'environnement

## Installation

```bash
# Créer et activer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate  # Sous Windows: .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configuration (facultatif)
cp .env.example .env
# Modifiez le fichier .env pour configurer votre clé API OpenAI et autres paramètres
```

## Utilisation

### Notebook Jupyter (recommandé pour l'analyse)

```bash
jupyter notebook
```

Le notebook `projet_minesweeper.ipynb` fournit une analyse détaillée du projet avec :
- Explications théoriques de la modélisation CSP
- Visualisations interactives des grilles et des contraintes
- Expérimentations systématiques avec différents paramètres
- Analyse statistique des performances
- Comparaison des approches CSP et LLM
- Études de cas et exemples concrets

### Interface graphique

```bash
python test.py
```

L'interface graphique permet de :
- Générer des grilles aléatoires avec des paramètres personnalisés
- Charger des grilles depuis des fichiers texte
- Jouer manuellement avec une interface graphique
- Résoudre les grilles avec le solveur CSP (mode pas à pas)
- Résoudre les grilles avec le solveur CSP + LLM (nécessite une clé API OpenAI)

### Interface en ligne de commande

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

#### Génération standard

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

#### Génération avec LLM

```bash
# Générer une grille avec un LLM (nécessite une clé API OpenAI)
python llm_grid_generator.py

# Personnaliser les paramètres
python llm_grid_generator.py --width 16 --height 16 --mines 40 --difficulty hard --pattern symmetrical

# Afficher la grille générée
python llm_grid_generator.py --display
```

Options spécifiques au générateur LLM :
- `--difficulty {easy,medium,hard,expert}` : Niveau de difficulté souhaité
- `--pattern PATTERN` : Motif spécifique (ex: symmetrical, corners, central)
- `--api-key API_KEY` : Clé API OpenAI (prioritaire sur .env)
- `--model MODEL` : Modèle à utiliser (défaut: gpt-3.5-turbo)

Le générateur LLM crée des grilles avec des motifs intéressants et des niveaux de difficulté spécifiques en demandant à un LLM de concevoir la disposition des mines. Le LLM prend en compte les contraintes du démineur pour générer des grilles jouables et résolvables par déduction logique.

### Utilisation en code Python

```python
from minesweeper import Minesweeper
from csp_solver import MinesweeperCSPSolver

# Créer une instance du jeu
game = Minesweeper(width=10, height=10, num_mines=15)

# Initialiser le solveur
solver = MinesweeperCSPSolver(game)

# Résoudre le jeu
safe_cells, mine_cells = solver.solve()

# Mettre à jour le jeu avec les résultats
solver.update_game(auto_play=True)
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

Pour utiliser les fonctionnalités basées sur les LLM (solveur CSP + LLM ou générateur de grilles LLM), vous devez configurer votre clé API OpenAI de l'une des façons suivantes :
1. Créer un fichier `.env` basé sur `.env.example` avec votre clé API
2. Définir la variable d'environnement `OPENAI_API_KEY`
3. La fournir directement aux constructeurs (`LLMCSPSolver(api_key="votre-clé-api")` ou `LLMGridGenerator(api_key="votre-clé-api")`)
4. La fournir lors de l'utilisation de l'interface en ligne de commande ou en argument aux scripts

Le fichier `.env` permet également de configurer d'autres paramètres comme le modèle à utiliser ou l'URL de base de l'API.

## Dépendances

- `numpy` : Gestion des tableaux et calculs numériques
- `matplotlib` : Visualisation des grilles
- `seaborn` : Visualisations statistiques avancées
- `pandas` : Analyse de données
- `scipy` : Analyse statistique
- `python-constraint` : Résolution du problème CSP
- `openai` : Communication avec les modèles OpenAI (optionnel)
- `python-dotenv` : Chargement des variables d'environnement
- `jupyter` et `notebook` : Environnement interactif
- `nbformat` : Création et manipulation de notebooks
- `PyQt6` : Interface graphique

## Références

- A Constraint-Based Approach to Solving Minesweeper (Bayer et Snyder, 2013)
- Minesweeper is NP-complete (Princeton, 2013)
- Documentation Jupyter Notebook : https://jupyter.org/documentation
- Documentation Matplotlib : https://matplotlib.org/stable/contents.html
- Documentation Seaborn : https://seaborn.pydata.org/ 