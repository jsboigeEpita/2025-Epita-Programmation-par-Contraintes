
# Documentation du Code

Ce dépôt contient du code Python illustrant différentes fonctionnalités liées à la gestion et la planification de tâches pour des robots sur une grille. Il comprend :

1. La définition de classes représentant des **tâches**, des **robots**, et la **grille**.
2. Un algorithme d’**A*** pour le pathfinding.
3. Une **solution de planification multi-agents** via **OR-Tools** (modèle CP-SAT).
4. Des **fonctions de visualisation** (affichage de trajectoires, Gantt charts, animations, etc.).

## Table des Matières

- [Aperçu des Classes](#aperçu-des-classes)
  - [Class `Task`](#class-task)
  - [Class `Robot`](#class-robot)
  - [Class `Grid`](#class-grid)
- [Fonctions Principales](#fonctions-principales)
  - [Pathfinding : `a_star_pathfinding`](#pathfinding--a_star_pathfinding)
  - [Planification Multi-Agents : `multi_agent_pathfinding`](#planification-multi-agents--multi_agent_pathfinding)
  - [Planification Multi-Agents Avancée : `multi_agent_pathfinding_with_energy_time`](#planification-multi-agents-avancée--multi_agent_pathfinding_with_energy_time)
  - [Planification de Tâches : `solve_robot_task_scheduling`](#planification-de-tâches--solve_robot_task_scheduling)
- [Fonctions de Visualisation](#fonctions-de-visualisation)
  - [`plot_paths`](#plot_paths)
  - [`plot_gantt_chart`](#plot_gantt_chart)
  - [`plot_paths_and_gantt`](#plot_paths_and_gantt)
  - [`display_animated_agent_moves`](#display_animated_agent_moves)
  - [`print_grid_with_paths`](#print_grid_with_paths)
- [Dépendances](#dépendances)
- [Exécution et Exemple d’Utilisation](#exécution-et-exemple-dutilisation)

---

## Aperçu des Classes

### Class `Task`

```python
class Task:
    def __init__(self, name, time, target_x, target_y, id, energy_cost=1):
        ...
```

- **Description** : Représente une tâche à réaliser.
- **Attributs** :
  - `name` : Nom de la tâche (string).
  - `duration` : Temps nécessaire pour exécuter la tâche (entier).
  - `target` : Coordonnées (x, y) où la tâche doit être accomplie.
  - `id` : Identifiant unique de la tâche.
  - `energy_cost` : Coût en énergie pour réaliser la tâche.
  - `completed` : Booléen indiquant si la tâche est complétée ou non.

### Class `Robot`

```python
class Robot:
    def __init__(self, x, y, base_station=None, max_energy=100, energy_consumption=1):
        ...
```

- **Description** : Représente un robot sur la grille.
- **Attributs** :

  - `current_position` : Position (x, y) actuelle.
  - `energy` : Énergie restante du robot.
  - `task` : Tâche en cours (ou `None` s’il n’y en a pas).
  - `task_complete` : Booléen indiquant si la tâche en cours est terminée.
  - `base_station` : Optionnel, indique une station de recharge.
  - `energy_consumption` : Taux de consommation d’énergie par unité de temps ou par mouvement.
- **Méthodes Principales** :

  - `set_task(task)`: Assigne une tâche au robot.
  - `complete_task(grid)`: Marque la tâche comme terminée.
  - `move(x, y)`: Déplace le robot d’une cellule (coût en énergie).
  - `perform_task(grid)`: Effectue l’ensemble du processus pour atteindre la position cible et accomplir la tâche.
  - `path_to_task(grid)`: Renvoie simplement le chemin (sous forme de liste de cellules) du robot vers la tâche assignée.

### Class `Grid`

```python
class Grid:
    def __init__(self, width, height, pattern='PV', nb_robots=0):
        ...
```

- **Description** : Représente la grille dans laquelle évoluent les robots.
- **Attributs** :
  - `width`, `height` : Dimensions de la grille.
  - `grid` : Liste 2D contenant le contenu de chaque cellule (ex. `' '`, `'R'`, `'C'`, `'@'`, etc.).
- **Méthodes Principales** :
  - `is_walkable(x, y)`: Indique si la cellule (x, y) est libre (pas un obstacle).
  - `place_robot(x, y, robot)`: Place un robot dans une cellule de la grille.
  - `place_task(x, y, task)`: Place une tâche dans la grille.
  - `print_grid()`: Affiche la grille dans la console.
  - `move_robot(robot, x, y)`: Met à jour la grille après le déplacement d’un robot.
  - `place_charging_station(x, y)`: Place une station de recharge à la position spécifiée.

---

## Fonctions Principales

### Pathfinding : `a_star_pathfinding`

```python
def a_star_pathfinding(start, goal, grid, empty_cell=0, obstacle_cell=1):
    ...
```

- **But** : Implémente l’algorithme A* pour trouver un chemin entre deux points (start et goal) dans la grille.
- **Paramètres** :
  - `start` : Tuple (x, y) de la position de départ.
  - `goal` : Tuple (x, y) de la position cible.
  - `grid` : Grille (2D) où chaque cellule peut être libre ou obstacle.
  - `empty_cell`, `obstacle_cell` : Symboles utilisés pour distinguer une cellule libre d’une cellule obstacle.
- **Retour** : Liste de tuples (x, y) représentant le chemin trouvé. Liste vide si pas de chemin.

### Planification Multi-Agents : `multi_agent_pathfinding`

```python
def multi_agent_pathfinding(agent_paths):
    ...
```

- **But** : Crée et résout un modèle **CP-SAT** (OR-Tools) pour empêcher les collisions entre plusieurs agents qui ont chacun un chemin défini.
- **Paramètres** :
  - `agent_paths` : Dictionnaire {agent_id : liste de cellules}.
- **Retour** : Un dictionnaire décrivant le planning (horaires) pour chaque agent si une solution est trouvée, ou `None` sinon.
- **Fonctionnement** :
  - Génère des variables intervalle par “segment” de chemin pour chaque agent.
  - Ajoute des contraintes de non-chevauchement dans la même cellule.
  - Minimise le makespan (temps total pour finir tous les déplacements).

### Planification Multi-Agents Avancée : `multi_agent_pathfinding_with_energy_time`

```python
def multi_agent_pathfinding_with_energy_time(agent_paths, initial_energies, energy_per_step, total_time_limit):
    ...
```

- **But** : Ajoute des **contraintes d’énergie** et de **temps** dans le modèle de planification multi-agents.
- **Paramètres** :
  - `agent_paths` : Dictionnaire {agent_id : liste de cellules}.
  - `initial_energies` : Dictionnaire {agent_id : énergie_initiale}.
  - `energy_per_step` : Coût en énergie par pas de déplacement.
  - `total_time_limit` : Limite de temps (horizon).
- **Retour** : Emploi du temps planifié ou informe qu’aucune solution n’a pu être trouvée.
- **Particularité** : Le modèle vérifie que chaque agent dispose de suffisamment d’énergie à chaque pas.

### Planification de Tâches : `solve_robot_task_scheduling`

```python
def solve_robot_task_scheduling(robots, tasks, total_time_limit):
    ...
```

- **But** : Assigne des tâches à des robots, en considérant la durée des tâches et l’énergie des robots via CP-SAT.
- **Paramètres** :
  - `robots` : Liste d’objets `Robot`.
  - `tasks` : Liste d’objets `Task`.
  - `total_time_limit` : Horizon temporel maximal (nombre entier).
- **Fonctionnement** :
  - Crée des variables booléennes `assignments[(r, t, time)]` indiquant si le robot `r` commence la tâche `t` à `time`.
  - Ajoute des contraintes :
    - Chaque tâche doit être effectuée exactement une fois.
    - Un robot ne peut faire qu’une seule tâche à la fois.
    - Vérification de la durée et de l’énergie disponibles.
- **Retour** : Un dictionnaire décrivant l’horaire de chaque robot pour les tâches assignées.

---

## Fonctions de Visualisation

### `plot_paths`

```python
def plot_paths(agent_paths):
    ...
```

- **But** : Affiche les trajectoires de plusieurs agents sur un plan (x, y) à l’aide de `matplotlib`.

### `plot_gantt_chart`

```python
def plot_gantt_chart(agent_paths, schedule):
    ...
```

- **But** : Génère un diagramme de Gantt (barres horizontales) pour chaque agent en fonction du planning.
- **Paramètres** :
  - `agent_paths` : Dictionnaire {agent_id : liste de cellules}.
  - `schedule` : Dictionnaire indiquant les temps de début pour chaque segment du chemin.

### `plot_paths_and_gantt`

```python
def plot_paths_and_gantt(agent_paths, schedule):
    ...
```

- **But** : Combine l’affichage des trajectoires et le diagramme de Gantt en deux sous-graphiques.

### `display_animated_agent_moves`

```python
def display_animated_agent_moves(agent_paths, schedule):
    ...
```

- **But** : Crée une animation montrant la progression de chaque agent au fil du temps sur la grille.

### `print_grid_with_paths`

```python
def print_grid_with_paths(grid, agent_paths):
    ...
```

- **But** : Affiche la grille dans la console, en colorant ou annotant les cases selon les chemins des agents (utilise `colorama`).

---

## Dépendances

- **Python 3.x**
- **OR-Tools** : `pip install ortools`
- **matplotlib**
- **colorama** (pour l’affichage coloré en console)
- **tabulate** (pour un affichage tabulaire de la grille)
- **collections**, **heapq**, etc. (librairies standard)
