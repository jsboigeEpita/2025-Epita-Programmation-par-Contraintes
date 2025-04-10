#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from ortools.graph import pywrapgraph
from ortools.sat.python import cp_model
from tabulate import tabulate


###############################################################################
# Définition des classes Grid, Robot, Task (reprend l'idée de robots.py)
###############################################################################

class Task:
    """Une tâche consiste à aller sur une position (x, y) et faire une action."""
    def __init__(self, name, time, target_x, target_y, id):
        self.id = id
        self.name = name
        self.duration = time
        self.completed = False
        # Position visée dans la grille (objectif)
        self.target = (target_x, target_y)

    def complete(self):
        self.completed = True


class Robot:
    id_counter = 0
    def __init__(self, x, y, base_station=None):
        self.current_position = (x, y)
        self.energy = 100
        self.inventory = []
        self.id = Robot.id_counter
        Robot.id_counter += 1

        self.max_inventory = 5
        self.task = None
        self.task_complete = False

        self.base_station = base_station

    def set_task(self, task):
        """Assigner une tâche à ce robot."""
        self.task = task
        self.task_complete = False

    def complete_task(self, grid):
        """Marque la tâche comme terminée."""
        if self.task is not None:
            self.task.complete()
            self.task_complete = True
            print(f"Robot {self.id} a terminé la tâche: {self.task.name}")
            self.task = None
            # return to base station
            path = find_path_with_ortools(grid, self.current_position, self.base_station)
            print(self.base_station)
            if path:
                for i in range(1, len(path)):
                    next_cell = path[i]
                    if self.energy <= 0:
                        print(f"Robot {self.id}: épuisé en chemin.")
                        return
                    self.move(next_cell[0], next_cell[1])
            
        else:
            print("Aucune tâche à terminer.")

    def move(self, x, y):
        """Effectuer un déplacement d’une case (coût en énergie)."""
        if self.energy > 0:
            self.current_position = (x, y)
            self.energy -= 1
        else:
            print(f"Robot {self.id}: plus assez d’énergie pour bouger.")

    def pick_up(self, item):
        if len(self.inventory) < self.max_inventory:
            self.inventory.append(item)
        else:
            print("Inventaire plein.")
    
    def drop(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
        else:
            print("Objet introuvable dans l’inventaire.")

    def perform_task(self, grid):
        """
        Fait en sorte que le robot :
         1) Trouve un chemin depuis sa position jusqu’à la position cible de la tâche.
         2) Se déplace pas à pas sur ce chemin.
         3) Complète la tâche.
        """
        if not self.task:
            print(f"Robot {self.id}: aucune tâche assignée.")
            return
        
        target_pos = self.task.target
        path = find_path_with_ortools(grid, self.current_position, target_pos)
        if not path:
            print(f"Robot {self.id}: impossible de trouver un chemin vers {target_pos}")
            return
        print(path)
        # Le chemin renvoyé inclut le nœud de départ et le nœud d’arrivée.
        # On va donc bouger pas à pas sur chaque segment
        for i in range(1, len(path)):
            next_cell = path[i]
            if self.energy <= 0:
                print(f"Robot {self.id}: épuisé en chemin.")
                return
            grid.move_robot(self, next_cell[0], next_cell[1])
            self.move(next_cell[0], next_cell[1])
            # print(f"Robot {self.id} se déplace vers {next_cell}")
            # grid.print_grid()
            # (on pourrait actualiser la grille visuelle, etc.)

        # Arrivé à destination, on finalise la tâche
        self.complete_task(grid)


class Grid:
    """
    Grille de base : 
      - ' ' case vide
      - 'R' obstacle (rack)
      - 'C' station de recharge
      - '🤖' robot (optionnel)
    """
    def __init__(self, width, height, pattern='PV', nb_robots=0):
        # Forçons width et height à être impairs, si besoin
        if width % 2 == 0:
            width += 1
        if height % 2 == 0:
            height += 1
        
        self.width = width
        self.height = height
        print(f"Grid size: {self.width} x {self.height}")

        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        if pattern == 'PV':
            # Place racks (R) verticalement par colonnes paires
            for i in range(1, height - 1):
                for j in range(1, width - 1, 2):
                    self.grid[i][j] = 'R'
        elif pattern == 'PH':
            # Place racks (R) horizontalement par lignes paires
            for i in range(1, height - 1, 2):
                for j in range(1, width - 1):
                    self.grid[i][j] = 'R'
        else:
            print("Pour simplifier, on ne gère que 'PV' et 'PH' ici.")
        # rajoute une zone de stockage en de dessous de la grille ou les robots se stockent apres avoir finis une tache
        robots_area = [' ' for _ in range(nb_robots)]
        self.grid.append(robots_area)


    def is_walkable(self, x, y):
        """Vrai si la case (x,y) est un espace vide, robot, ou charge, etc. => pas un rack."""
        if x < 0 or x >= self.height or y < 0 or y >= self.width:
            return False
        cell = self.grid[x][y]
        if cell == 'R':
            return False
        return True

    def place_robot(self, x, y, robot):
        if self.grid[x][y] == ' ':
            self.grid[x][y] = '🤖'
            robot.current_position = (x, y)
        else:
            print("Cellule déjà occupée.")


    def print_grid(self):
        """
        Affiche la grille en utilisant tabulate pour un affichage plus lisible.
        """
        headers = [f"{j}" for j in range(self.width)]  # Column headers
        table = [[f"{i}"] + row for i, row in enumerate(self.grid)]  # Add row headers
        print(tabulate(table, headers=[" "] + headers, tablefmt="grid"))
    
    def move_robot(self, robot, x, y):
        if self.grid[x][y] == ' ':
            # Retirer le robot de sa position actuelle
            (rx, ry) = robot.current_position
            self.grid[rx][ry] = ' '
            # Placer le robot à la nouvelle position
            self.grid[x][y] = '🤖'
            robot.current_position = (x, y)
        else:
            print("Cellule déjà occupée.")

    def place_charging_station(self, x, y):
        if self.grid[x][y] == ' ':
            self.grid[x][y] = 'C'
        else:
            print("Cellule déjà occupée.")


###############################################################################
# Fonction de pathfinding avec OR-Tools (min cost flow)
###############################################################################

def find_path_with_ortools(grid, start, goal):
    """
    Trouver un chemin minimal (en nombre de pas) sur la grille `grid` 
    entre la case start=(sx, sy) et goal=(gx, gy), 
    en utilisant le MinCostFlow de OR-Tools comme un solveur de plus court chemin.

    Retourne une liste de tuples (x, y) décrivant le chemin, 
    y compris la case de départ et la case d'arrivée.
    Retourne [] si pas de chemin.
    """
    (sx, sy) = start
    (gx, gy) = goal

    # Vérifions d'abord si les positions sont "walkable"
    if not grid.is_walkable(sx, sy) or not grid.is_walkable(gx, gy):
        return []

    # Identifions la taille de la grille
    H = grid.height
    W = grid.width

    # Fonction pour transformer (x, y) en identifiant de nœud unique
    def node_id(x, y):
        return x * W + y

    start_node = node_id(sx, sy)
    goal_node = node_id(gx, gy)

    # On crée l'objet MinCostFlow
    min_cost_flow = pywrapgraph.SimpleMinCostFlow()

    # Parcourons la grille pour ajouter des arcs (capacité=1, coût=1) 
    # entre cases voisines (haut, bas, gauche, droite) autorisées.
    # Cela revient à un graphe non orienté => on ajoute arcs dans les 2 sens.
    for x in range(H):
        for y in range(W):
            if grid.is_walkable(x, y):
                u = node_id(x, y)
                # Voisins potentiels
                neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                for (nx, ny) in neighbors:
                    if 0 <= nx < H and 0 <= ny < W and grid.is_walkable(nx, ny):
                        v = node_id(nx, ny)
                        # On ajoute l'arc u->v
                        # capacity = 1, cost = 1
                        min_cost_flow.AddArcWithCapacityAndUnitCost(u, v, 1, 1)
                        # Pour un graphe non orienté, on ajoute aussi v->u 
                        min_cost_flow.AddArcWithCapacityAndUnitCost(v, u, 1, 1)

    # On fixe l'offre de 1 unité au start_node et la demande de 1 unité au goal_node
    for n in range(H * W):
        if n == start_node:
            min_cost_flow.SetNodeSupply(n, 1)
        elif n == goal_node:
            min_cost_flow.SetNodeSupply(n, -1)
        else:
            min_cost_flow.SetNodeSupply(n, 0)

    # On résout
    status = min_cost_flow.Solve()
    if status != min_cost_flow.OPTIMAL:
        # Pas de chemin trouvé
        return []

    # Sinon, on sait qu'il y a un flux de 1 unité entre start_node et goal_node.
    # Pour reconstruire le chemin, on va repérer les arcs où le flux = 1.
    # On aura un "chemin" en mode fil d'Ariane, mais ce n’est pas trivial 
    # si l’on ne stocke pas la parenté. On va construire un graphe 
    # d’adjacences "flow" pour retrouver le chemin.
    flow_graph = {}
    for i in range(min_cost_flow.NumArcs()):
        flow = min_cost_flow.Flow(i)
        if flow > 0:
            # Arc (u->v) où flow=1
            u = min_cost_flow.Tail(i)
            v = min_cost_flow.Head(i)
            # On retient cet arc comme "u -> v"
            flow_graph[u] = v

    # Reconstruisons le chemin en partant de start_node, 
    # en suivant flow_graph[u] -> v jusqu’au goal_node.
    path = [start_node]
    current = start_node
    while current in flow_graph:
        nxt = flow_graph[current]
        path.append(nxt)
        if nxt == goal_node:
            break
        current = nxt

    # Si on n'atteint pas goal_node, c’est un échec.
    if path[-1] != goal_node:
        return []

    # Convertissons les indices de nœuds en coordonnées (x, y)
    coords_path = []
    for nid in path:
        x_coord = nid // W
        y_coord = nid % W
        coords_path.append((x_coord, y_coord))

    return coords_path

def assign_tasks(robots, tasks, max_time):
    """
    Résout un problème d'assignation de 'tasks' à des 'robots', 
    de manière à ce que toutes les tâches soient terminées avant 'max_time'.

    :param robots: liste d'objets Robot (avec un champ 'id')
    :param tasks: liste d'objets Task (avec 'id', 'duration')
    :param max_time: temps maximum (makespan imposé) d'achèvement de toutes les tâches
    :return: 
       - un dictionnaire indiquant pour chaque tâche 
         [le robot assigné, l'heure de début, l'heure de fin], 
         ou None si pas de solution.
    """
    model = cp_model.CpModel()

    # Raccourcis
    num_robots = len(robots)
    num_tasks = len(tasks)
    robot_ids = [r.id for r in robots]
    task_ids = [t.id for t in tasks]

    # Pour simplifier, on crée un mapping "index -> robot_id" et inversement
    # si besoin. Ici, on suppose que robot_ids = [0,1,2,...].
    # Idem pour task_ids.
    # Sinon, on fera un mapping via des dict.
    
    # Variables de décision x[t, r] = 1 si la tâche t est effectuée par le robot r
    x = {}
    for t in task_ids:
        for r in robot_ids:
            x[(t, r)] = model.NewBoolVar(f"x_t{t}_r{r}")
    
    # Variables temporelles: start[t, r] et end[t, r], 
    # plus un IntervalVar "optionnel" pour représenter la tâche t si faite par r
    start = {}
    end = {}
    intervals = {}
    
    # On crée un dictionnaire "durée" pour accéder plus facilement
    durations = {}
    for task in tasks:
        durations[task.id] = task.duration

    # Bornes sup sur le temps (0 <= start, end <= max_time)
    for t in task_ids:
        for r in robot_ids:
            start[(t, r)] = model.NewIntVar(0, max_time, f"start_t{t}_r{r}")
            end[(t, r)]   = model.NewIntVar(0, max_time, f"end_t{t}_r{r}")
            intervals[(t, r)] = model.NewOptionalIntervalVar(
                start[(t, r)],
                durations[t],
                end[(t, r)],
                x[(t, r)],
                f"interval_t{t}_r{r}"
            )
    
    # 1) Chaque tâche doit être assignée à exactement un robot
    for t in task_ids:
        model.Add(sum(x[(t, r)] for r in robot_ids) == 1)

    # 2) Ordonnancement: sur chaque robot, pas de chevauchement dans le temps
    for r in robot_ids:
        # Récupère toutes les IntervalVar associées à ce robot
        interval_list = [intervals[(t, r)] for t in task_ids]
        model.AddNoOverlap(interval_list)
    
    # 3) Respect de la deadline globale: end[t,r] <= max_time si x[t,r] = 1
    #    => end[t,r] <= max_time + M*(1 - x[t,r])  (où M est grand)
    #    Pour simplifier, on peut imposer end[t,r] <= max_time directement 
    #    ET s'assurer que x[t,r] = 1 => end[t,r] <= max_time
    #    ce qui revient au même si on borne end[t,r].
    for t in task_ids:
        for r in robot_ids:
            # Fin de tâche <= max_time
            model.Add(end[(t, r)] <= max_time).OnlyEnforceIf(x[(t, r)])
            # On peut relâcher la contrainte si x[t,r] = 0, 
            # mais on a déjà borné end[t,r] <= max_time ci-dessus. 
            # Donc c'est suffisant.

    # 4) On ne cherche pas forcément à minimiser le makespan (puisqu'il est imposé),
    #    on cherche simplement la faisabilité. 
    #    Si vous voulez minimiser le nombre de robots occupés, ou autre, 
    #    vous pouvez ajouter un objectif. 
    #    Ici, on va juste demander un "feasible solution".
    model.Minimize(0)  # Aucune fonction objectif, ou Minimiser(0) => on veut juste un plan faisable
    
    # Résolution
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # On construit la solution
        assignment = {}
        for t in task_ids:
            for r in robot_ids:
                if solver.Value(x[(t, r)]) == 1:
                    st = solver.Value(start[(t, r)])
                    en = solver.Value(end[(t, r)])
                    assignment[t] = {
                        "robot": r,
                        "start": st,
                        "end": en
                    }
                    break
        return assignment
    else:
        print("Aucune solution réalisable pour le temps imposé.")
        return None


###############################################################################
# Exemple d’utilisation
###############################################################################
def scenario_1():
    """
    Scénario 1 : Un robot doit aller chercher un colis à une position donnée.
    """
    # 1) Créer une grille (hauteur=7, largeur=9) et un pattern de racks
    g = Grid(8, 7, pattern='PH')

    # 2) Créer un robot et le placer en (0,0)
    robot = Robot(0, 0)
    g.place_robot(0, 0, robot)

    # 3) Créer une tâche "Aller prendre un colis" à la position (5,6)
    task = Task("Aller chercher un colis", time=5, target_x=4, target_y=3)
    robot.set_task(task)

    # 4) Affichage initial
    print("\n--- Grille initiale ---")
    g.print_grid()

    # 5) Faire exécuter la tâche par le robot
    print("\n--- Le robot exécute sa tâche ---")
    robot.perform_task(g)

    # 6) Résultat
    print("\n--- État final ---")
    print(f"Robot position finale: {robot.current_position}")
    print(f"Tâche accomplie ? {task.completed}")
    print(f"Énergie restante robot: {robot.energy}")

def scenario_2():
    
    # Scenario 2 : 5 robots avec 3 tâches
    # 1) Créer une grille (hauteur=7, largeur=9) et un pattern de racks
    g = Grid(8, 7, pattern='PH')
    # 2) Créer 5 robots et les placer en (0,0), (0,1), (0,2), (0,3), (0,4)
    robots = [Robot(0, i) for i in range(5)]
    for i, robot in enumerate(robots):
        g.place_robot(0, i, robot)
    # 3) Créer 3 tâches à des positions différentes
    tasks = [
        Task("Tâche 1", time=5, target_x=4, target_y=3, id=1),
        Task("Tâche 2", time=5, target_x=4, target_y=5, id=2),
        Task("Tâche 3", time=5, target_x=6, target_y=2, id=3)
    ]

    # 4) Assigner les tâches aux robots
    for i, robot in enumerate(robots):
        if i < len(tasks):
            robot.set_task(tasks[i])
        else:
            robot.set_task(None)
    # 5) Affichage initial
    print("\n--- Grille initiale ---")
    g.print_grid()
    # 6) Faire exécuter les tâches par les robots
    print("\n--- Les robots exécutent leurs tâches ---")
    for robot in robots:
        robot.perform_task(g)
    # 7) Résultat
    print("\n--- État final ---")
    for robot in robots:
        print(f"Robot {robot.id} position finale: {robot.current_position}")
        print(f"Tâche accomplie ? {robot.task.completed if robot.task else 'Aucune tâche'}")
        print(f"Énergie restante robot: {robot.energy}")
    # 8) Affichage final
    print("\n--- Grille finale ---")
    g.print_grid()
    # 9) Affichage des tâches restantes
    remaining_tasks = [task for task in tasks if not task.completed]   
    if remaining_tasks:
        print("\n--- Tâches restantes ---")
        for task in remaining_tasks:
            print(f"Tâche {task.name} non accomplie à la position {task.target}")
    else:
        print("\n--- Toutes les tâches ont été accomplies ! ---")
    # 10) Affichage de la grille finale
    g.print_grid()

def scenario_3():
    # Scenario 3 : 5 robots avec 5 tâches et un temps maximum
    # On utilise l'assignation de tâches avec OR-Tools
    # 1) Créer une grille (hauteur=20, largeur=20) et un pattern de racks
    h = 20
    l = 20
    g = Grid(h, l, pattern='PH')
    # 2) Créer 5 robots et les placer en (0,0), (0,1), (0,2), (0,3), (0,4)
    robots = [Robot(0, i,(i, h-1)) for i in range(1)]
    print("\n--- Robots ---")
    for robot in robots:
        print(f"Robot {robot.id} position initiale: {robot.current_position}")
        print(f"Base station: {robot.base_station}")
    for i, robot in enumerate(robots):
        g.place_robot(0, i, robot)
    # 3) Créer 10 tâches à des positions différentes
    tasks = []
    tasks.append(Task("Tâche 1", time=5, target_x=2, target_y=4, id=1))
    tasks.append(Task("Tâche 2", time=3, target_x=4, target_y=5, id=2))
    tasks.append(Task("Tâche 3", time=1, target_x=6, target_y=2, id=3))
    tasks.append(Task("Tâche 4", time=5, target_x=6, target_y=4, id=4))
    tasks.append(Task("Tâche 5", time=5, target_x=6, target_y=6, id=5))     
    # print("\n--- Tâches à accomplir ---")
    # for task in tasks:
    #     print(f"{task.name} {task.target} (durée: {task.duration})")

    task_assignment = assign_tasks(robots, tasks, max_time=100)
    # print(task_assignment)
    if task_assignment:
        print("\n--- Tâches assignées ---")
        for task_id, assignment in task_assignment.items():
            robot_id = assignment["robot"]
            start_time = assignment["start"]
            end_time = assignment["end"]
            print(f"Tâche {task_id} <--> robot {robot_id} de {start_time} à {end_time}")
            # On assigne la tâche au robot
            robot = robots[robot_id]
            task = next(t for t in tasks if t.id == task_id)
            robot.set_task(task)
    else:
        print("Aucune tâche assignée.")
    # 4) Affichage initial
    print("\n--- Grille initiale ---")
    g.print_grid()
    # 5) Faire exécuter les tâches par les robots
    print("\n--- Les robots exécutent leurs tâches ---")
    for robot in robots:
        robot.perform_task(g)
    # 6) Résultat
    print("\n--- État final ---")
    for robot in robots:
        print(f"Robot {robot.id} position finale: {robot.current_position}")
        print(f"Tâche accomplie ? {robot.task.completed if robot.task else 'Aucune tâche'}")
        print(f"Énergie restante robot: {robot.energy}")
        print("---------------")
    # 7) Affichage final
    print("\n--- Grille finale ---")
    g.print_grid()

if __name__ == "__main__":
    # print("=== Scénario 1 ===")
    # scenario_1()  
    # print("=== Scénario 2 ===")
    # scenario_2()
    print("=== Scénario 3 ===")
    scenario_3()

