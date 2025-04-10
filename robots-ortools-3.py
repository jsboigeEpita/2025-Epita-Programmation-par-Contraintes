from ortools.sat.python import cp_model
from collections import defaultdict
from heapq import heappop, heappush
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tabulate import tabulate

class Task:
    """Une tâche consiste à aller sur une position (x, y) et faire une action."""
    def __init__(self, name, time, target_x, target_y, id, energy_cost=1):
        self.id = id
        self.name = name
        self.duration = time
        self.completed = False
        # Position visée dans la grille (objectif)
        self.target = (target_x, target_y)
        self.energy_cost = energy_cost

    def complete(self):
        self.completed = True


class Robot:
    id_counter = 0
    def __init__(self, x, y, base_station=None, max_energy=100, energy_consumption=1):
        self.current_position = (x, y)
        self.energy = max_energy
        self.energy_consumption = energy_consumption
        self.id = Robot.id_counter
        Robot.id_counter += 1

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
        path = a_star_pathfinding(self.current_position, target_pos, grid.grid, empty_cell=' ', obstacle_cell='R')
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
    def path_to_task(self, grid):
        """
        Trouve le chemin vers la tâche assignée.
        """
        if self.task:
            target_pos = self.task.target
            path = a_star_pathfinding(self.current_position, target_pos, grid.grid, empty_cell=' ', obstacle_cell='R')
            return path
        else:
            print(f"Robot {self.id}: aucune tâche assignée.")
            return None

class Grid:
    """
    Grille de base : 
      - ' ' case vide
      - 'R' obstacle (rack)
      - 'C' station de recharge
      - '@' robot (optionnel)
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
        elif pattern == 'R':
            # Place racks (R) aléatoirement
            import random
            for i in range(1, height - 1):
                for j in range(1, width - 1):
                    if random.random() < 0.2:
                        self.grid[i][j] = 'R'
        elif pattern == 'PH2':
            # Place racks (R) rangé d'epaisseur 2
            for i in range(1, height - 1, 2):
                for j in range(1, width - 1, 2):
                    self.grid[i][j] = 'R'
        else:
            print("Pour simplifier, on ne gère que 'PV' et 'PH' ici.")


    def is_walkable(self, x, y):
        """Vrai si la case (x,y) est un espace vide, robot, ou charge, etc. => pas un rack."""
        if x < 0 or x >= self.height or y < 0 or y >= self.width:
            return False
        cell = self.grid[x][y]
        if cell == 'R':
            return False
        return True

    def place_robot(self, x, y, robot):
        if self.grid[x][y] == ' ' or 'T' in self.grid[x][y]:
            self.grid[x][y] = '@'
            robot.current_position = (x, y)
        else:
            print("Cellule déjà occupée.")

    def place_task(self, x, y, task):
        if self.grid[x][y] == ' ':
            self.grid[x][y] = 'T' + str(task.id)
        else:
            self.grid[x][y] = self.grid[x][y] + 'T' + str(task.id)

    def print_grid(self):
        """
        Affiche la grille en utilisant tabulate pour un affichage plus lisible.
        """
        headers = [f"{j}" for j in range(self.width)]  # Column headers
        table = [[f"{i}"] + row for i, row in enumerate(self.grid)]  # Add row headers
        print(tabulate(table, headers=[" "] + headers, tablefmt="grid"))
    
    def move_robot(self, robot, x, y):
        if self.grid[x][y] == ' ' or 'T' in self.grid[x][y]:
            # Retirer le robot de sa position actuelle
            (rx, ry) = robot.current_position
            self.grid[rx][ry] = ' '
            # Placer le robot à la nouvelle position
            self.grid[x][y] = '@'
            robot.current_position = (x, y)
        else:
            print("Cellule déjà occupée.")

    def place_charging_station(self, x, y):
        if self.grid[x][y] == ' ':
            self.grid[x][y] = 'C'
        else:
            print("Cellule déjà occupée.")


def multi_agent_pathfinding(agent_paths):
    """
    Given a dictionary `agent_paths` that maps:
        agent_id -> [ (x1,y1), (x2,y2), (x3,y3), ... ]
    describing each agent's path (sequence of grid cells),
    build and solve a CP-SAT model that enforces no collisions.
    """

    model = cp_model.CpModel()

    # A horizon that is at least as large as the number of steps by the 'longest' agent path
    # (You can make this bigger if you want to allow waiting, but here we do no-wait.)
    max_steps = max(len(path) for path in agent_paths.values())
    horizon = max_steps  # each step takes 1 time unit, ignoring wait

    # We will store the IntervalVars, plus associated start/end in dictionaries
    intervals_by_cell = defaultdict(list)  # cell -> list of IntervalVars
    start_vars = {}  # (agent, step_index) -> start_var
    end_vars = {}    # (agent, step_index) -> end_var

    # Build intervals for each step in each agent's path
    for agent, path in agent_paths.items():
        # path is e.g. [(x0,y0), (x1,y1), (x2,y2), ...]

        # We consider "arcs" between consecutive cells.
        # If path has N cells, it has (N-1) arcs (steps).
        for step_index in range(len(path) - 1):
            # The new cell the agent will occupy after moving from path[step_index]
            cell_occupied = path[step_index + 1]

            # Create start and end variables for occupying that cell
            start_var = model.NewIntVar(0, horizon, f"start_a{agent}_s{step_index}")
            end_var   = model.NewIntVar(0, horizon, f"end_a{agent}_s{step_index}")

            # Duration is 1 time unit
            interval_var = model.NewIntervalVar(start_var, 1, end_var,
                                                f"interval_a{agent}_s{step_index}")

            # Record them
            start_vars[(agent, step_index)] = start_var
            end_vars[(agent, step_index)]   = end_var

            # Track that this interval occupies the given cell
            intervals_by_cell[cell_occupied].append(interval_var)

            # If this is not the first step, chain it to the previous step:
            if step_index > 0:
                # end of previous step == start of this step
                model.Add(start_var == end_vars[(agent, step_index - 1)])
    
    # Add the collision avoidance: NoOverlap per cell
    for cell, intervals in intervals_by_cell.items():
        if len(intervals) > 1:
            # If only 1 interval uses a cell, no overlap constraint is trivial
            model.AddNoOverlap(intervals)

    # (Optional) Minimizing the overall makespan
    # That is, the time at which the last agent finishes its last step
    all_end_vars = []
    for agent, path in agent_paths.items():
        if len(path) > 1:
            last_step = len(path) - 2  # if path has N cells, last step index is N-2
            all_end_vars.append(end_vars[(agent, last_step)])
    makespan = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(makespan, all_end_vars)
    model.Minimize(makespan)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"Solution status: {solver.StatusName(status)}")
        print(f"Objective (Makespan) = {solver.Value(makespan)}\n")
        # Extract the actual schedule
        schedule = defaultdict(list)
        for agent, path in agent_paths.items():
            print(f"Agent {agent}:")
            if len(path) < 2:
                # No movement if the path has only one cell
                print(f"  Path has only one cell: {path[0]}")
                continue
            
            agent_schedule = []
            for step_index in range(len(path) - 1):
                s = solver.Value(start_vars[(agent, step_index)])
                e = solver.Value(end_vars[(agent, step_index)])
                origin_cell = path[step_index]
                dest_cell   = path[step_index + 1]
                print(f"  Step {step_index} from {origin_cell} -> {dest_cell}, "
                      f"occupy {dest_cell} in [{s}, {e})")
                agent_schedule.append(s)
            schedule[agent] = agent_schedule
            print()
        # print the object description
        print("Agent paths and schedules:")
        for agent, path in agent_paths.items():
            print(f"Agent {agent}: Path: {path}, Schedule: {schedule[agent]}")
        return schedule  # Return the schedule for each agent
    else:
        print("No feasible solution found.")

# Do not work
def multi_agent_pathfinding_with_energy_time(agent_paths, initial_energies, energy_per_step, total_time_limit):
    """
    Given a dictionary `agent_paths` that maps:
        agent_id -> [ (x1,y1), (x2,y2), (x3,y3), ... ]
    describing each agent's path (sequence of grid cells),
    build and solve a CP-SAT model that enforces no collisions,
    energy constraints, and time constraints.
    """

    model = cp_model.CpModel()

    # A horizon that is at least as large as the number of steps by the 'longest' agent path
    # (You can make this bigger if you want to allow waiting, but here we do no-wait.)
    max_steps = max(len(path) for path in agent_paths.values())
    horizon = min(max_steps, total_time_limit)  # each step takes 1 time unit, ignoring wait

    # We will store the IntervalVars, plus associated start/end in dictionaries
    intervals_by_cell = defaultdict(list)  # cell -> list of IntervalVars
    start_vars = {}  # (agent, step_index) -> start_var
    end_vars = {}    # (agent, step_index) -> end_var
    energy_vars = {} # (agent, time) -> energy_var

    # Build intervals for each step in each agent's path
    for agent, path in agent_paths.items():
        # path is e.g. [(x0,y0), (x1,y1), (x2,y2), ...]

        # We consider "arcs" between consecutive cells.
        # If path has N cells, it has (N-1) arcs (steps).
        for step_index in range(len(path) - 1):
            # The new cell the agent will occupy after moving from path[step_index]
            cell_occupied = path[step_index + 1]

            # Create start and end variables for occupying that cell
            start_var = model.NewIntVar(0, horizon, f"start_a{agent}_s{step_index}")
            end_var   = model.NewIntVar(0, horizon, f"end_a{agent}_s{step_index}")

            # Duration is 1 time unit
            interval_var = model.NewIntervalVar(start_var, 1, end_var,
                                                f"interval_a{agent}_s{step_index}")

            # Record them
            start_vars[(agent, step_index)] = start_var
            end_vars[(agent, step_index)]   = end_var

            # Track that this interval occupies the given cell
            intervals_by_cell[cell_occupied].append(interval_var)

            # If this is not the first step, chain it to the previous step:
            if step_index > 0:
                # end of previous step == start of this step
                model.Add(start_var == end_vars[(agent, step_index - 1)])

        # Energy Constraint
        for time in range(horizon + 1):
            energy_vars[(agent, time)] = model.NewIntVar(0, initial_energies[agent], f"energy_a{agent}_t{time}")

        # Initial energy
        model.Add(energy_vars[(agent, 0)] == initial_energies[agent])

        # Energy consumption
        for step_index in range(len(path) - 1):
            for time in range(horizon):
                # If the agent is doing this step at this time
                is_doing_step = model.NewBoolVar(f"is_doing_step_a{agent}_s{step_index}_t{time}")
                model.Add(start_vars[(agent, step_index)] == time).OnlyEnforceIf(is_doing_step)
                model.Add(start_vars[(agent, step_index)] != time).OnlyEnforceIf(is_doing_step.Not())

                # If the agent is doing this step, it consumes energy
                model.Add(energy_vars[(agent, time + 1)] == energy_vars[(agent, time)] - energy_per_step).OnlyEnforceIf(is_doing_step)
                # If the agent is not doing this step, it does not consume energy
                model.Add(energy_vars[(agent, time + 1)] == energy_vars[(agent, time)]).OnlyEnforceIf(is_doing_step.Not())

                # Energy cannot be negative
                model.Add(energy_vars[(agent, time)] >= 0)
        # Energy consumption : the agent cannot do a step if it doesn't have enough energy
        for step_index in range(len(path) - 1):
            # Energy consumption: the agent cannot do a step if it doesn't have enough energy
            for step_index in range(len(path) - 1):
                for time in range(horizon):
                    # Create a Boolean variable to represent insufficient energy
                    insufficient_energy = model.NewBoolVar(f"insufficient_energy_a{agent}_t{time}")

                    # Add constraints to set the Boolean variable based on energy levels
                    model.Add(energy_vars[(agent, time)] < energy_per_step).OnlyEnforceIf(insufficient_energy)
                    model.Add(energy_vars[(agent, time)] >= energy_per_step).OnlyEnforceIf(insufficient_energy.Not())

                    # Prevent the agent from starting the step if energy is insufficient
                    model.Add(start_vars[(agent, step_index)] != time).OnlyEnforceIf(insufficient_energy)

    # Add the collision avoidance: NoOverlap per cell
    for cell, intervals in intervals_by_cell.items():
        if len(intervals) > 1:
            # If only 1 interval uses a cell, no overlap constraint is trivial
            model.AddNoOverlap(intervals)

    # (Optional) Minimizing the overall makespan
    # That is, the time at which the last agent finishes its last step
    all_end_vars = []
    for agent, path in agent_paths.items():
        if len(path) > 1:
            last_step = len(path) - 2  # if path has N cells, last step index is N-2
            all_end_vars.append(end_vars[(agent, last_step)])
    makespan = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(makespan, all_end_vars)
    model.Minimize(makespan)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"Solution status: {solver.StatusName(status)}")
        print(f"Objective (Makespan) = {solver.Value(makespan)}\n")
        # Extract the actual schedule
        schedule = defaultdict(list)
        for agent, path in agent_paths.items():
            print(f"Agent {agent}:")
            if len(path) < 2:
                # No movement if the path has only one cell
                print(f"  Path has only one cell: {path[0]}")
                continue
            
            agent_schedule = []
            for step_index in range(len(path) - 1):
                s = solver.Value(start_vars[(agent, step_index)])
                e = solver.Value(end_vars[(agent, step_index)])
                origin_cell = path[step_index]
                dest_cell   = path[step_index + 1]
                print(f"  Step {step_index} from {origin_cell} -> {dest_cell}, "
                      f"occupy {dest_cell} in [{s}, {e})")
                agent_schedule.append(s)
            schedule[agent] = agent_schedule
            print()
            for time in range(horizon + 1):
                print(f"  Energy at time {time}: {solver.Value(energy_vars[(agent, time)])}")
        # print the object description
        print("Agent paths and schedules:")
        for agent, path in agent_paths.items():
            print(f"Agent {agent}: Path: {path}, Schedule: {schedule[agent]}")
        return schedule  # Return the schedule for each agent
    else:
        print("No feasible solution found.")

def a_star_pathfinding(start, goal, grid, empty_cell=0, obstacle_cell=1):
    """
    A* pathfinding algorithm to find the shortest path from start to goal on a grid.
    :param start: Tuple (x, y) representing the starting position.
    :param goal: Tuple (x, y) representing the goal position.
    :param grid: 2D list where 0 represents a free cell and 1 represents an obstacle.
    :return: List of tuples representing the path from start to goal, or an empty list if no path exists.
    """
    # print(f"Start: {start}, Goal: {goal}")
    # print(f"Grid: {grid}")
    def heuristic(a, b):
        # Manhattan distance heuristic
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    rows, cols = len(grid), len(grid[0])
    open_set = []
    heappush(open_set, (0, start))  # Priority queue with (cost, position)
    came_from = {}  # To reconstruct the path
    g_score = {start: 0}  # Cost from start to current node
    f_score = {start: heuristic(start, goal)}  # Estimated cost from start to goal

    while open_set:
        _, current = heappop(open_set)

        if current == goal:
            # Reconstruct the path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]  # Return reversed path

        x, y = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Neighboring cells (up, down, left, right)
            neighbor = (x + dx, y + dy)
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and (grid[neighbor[0]][neighbor[1]] == empty_cell or (neighbor[0] == goal[0] and neighbor[1] == goal[1]) or (grid[neighbor[0]][neighbor[1]] == '@')):
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heappush(open_set, (f_score[neighbor], neighbor))

    return []  # Return an empty list if no path is found

def solve_robot_task_scheduling(robots, tasks, total_time_limit):
    model = cp_model.CpModel()

    # 1. Data
    all_robots = range(len(robots))
    all_tasks = range(len(tasks))
    all_time_slots = range(total_time_limit)  # Time slots from 0 to total_time_limit - 1

    # 2. Variables
    assignments = {}
    for r in all_robots:
        for t in all_tasks:
            for time in all_time_slots:
                assignments[(r, t, time)] = model.NewBoolVar(f"assign_r{r}_t{t}_time{time}")

    # 3. Constraints
    # Each task must be assigned to exactly one robot in one time slot
    for t in all_tasks:
        model.AddExactlyOne(assignments[(r, t, time)] for r in all_robots for time in all_time_slots)

    # A robot can only perform one task at a time
    for r in all_robots:
        for time in all_time_slots:
            model.AddAtMostOne(assignments[(r, t, time)] for t in all_tasks)

    # Time Constraint:
    # A robot cannot start a task if it doesn't have enough time to complete it
    for r in all_robots:
        for t in all_tasks:
            for time in all_time_slots:
                if time + tasks[t].duration > total_time_limit:
                    model.Add(assignments[(r, t, time)] == 0)

    # A robot can only do one task at a time
    for r in all_robots:
        for time in all_time_slots:
            for t1 in all_tasks:
                for t2 in all_tasks:
                    if t1 != t2:
                        for time2 in range(time, min(time + tasks[t1].duration, total_time_limit)):
                            model.Add(assignments[(r, t1, time)] + assignments[(r, t2, time2)] <= 1)

    # Energy Constraint:
    # A robot must have enough energy to perform a task
    for r in all_robots:
        for t in all_tasks:
            for time in all_time_slots:
                # Calculate the energy needed for the task and the time it takes
                energy_needed = tasks[t].energy_cost + tasks[t].duration * robots[r].energy_consumption
                # Check if the robot has enough energy at the start of the task
                model.Add(assignments[(r, t, time)] == 0).OnlyEnforceIf(robots[r].energy < energy_needed)

    # ... (Add other constraints: inventory, travel, etc.)

    # 4. Objective (Optional)
    # ... (Define an objective function)

    # 5. Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Build a schedule
    schedule = defaultdict(list)

    # 6. Interpret Solution
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for r in all_robots:
            for t in all_tasks:
                for time in all_time_slots:
                    if solver.Value(assignments[(r, t, time)]) == 1:
                        print(f"Robot {robots[r].id} assigned to Task {tasks[t].id} at time {time} for {tasks[t].duration} time units. Energy cost : {tasks[t].energy_cost}")
                        schedule[robots[r].id].append((tasks[t], time))
        print("Schedule:")
        for robot_id, tasks in schedule.items():
            print(f"Robot {robot_id}:")
            for task, time in tasks:
                print(f"  Task {task.id} at time {time} (duration: {task.duration})")
        return schedule
    else:
        print("No solution found.")

def plot_paths(agent_paths):
    """
    Visualize the paths of agents on a grid.
    This function uses matplotlib to plot the paths.
    """

    plt.figure(figsize=(8, 8))
    for agent, path in agent_paths.items():
        x, y = zip(*path)
        plt.plot(x, y, marker='o', label=f'Agent {agent}')
    
    plt.title('Agent Paths')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.legend()
    plt.show()

def plot_gantt_chart(agent_paths, schedule):
    """
    Plot a Gantt chart for the schedule of each agent's path.
    This function uses matplotlib to create a Gantt chart.
    """

    plt.figure(figsize=(10, 6))
    for agent, path in agent_paths.items():
        print(f"Agent {agent} schedule: {schedule[agent]}")
        for step_index in range(len(path) - 1):
            start_time = schedule[agent][step_index]
            end_time = start_time + 1  # Each step takes 1 time unit
            print(f"Step {step_index}: start={start_time}, end={end_time}")
            plt.barh(f"Agent {agent}", end_time - start_time, left=start_time, color=f"C{agent}", edgecolor='black')
    
    plt.title('Gantt Chart of Agent Paths')
    plt.xlabel('Time')
    plt.ylabel('Agents')
    plt.grid(True)
    plt.show()

def plot_paths_and_gantt(agent_paths,schedule):
    """
    Visualize the paths of agents and their Gantt chart in the same figure.
    This function combines the path visualization and Gantt chart.
    """
    fig, ax = plt.subplots(2, 1, figsize=(10, 12))

    # Plot paths
    for agent, path in agent_paths.items():
        x, y = zip(*path)
        ax[0].plot(x, y, marker='o', label=f'Agent {agent}')
    
    ax[0].set_title('Agent Paths')
    ax[0].set_xlabel('X Coordinate')
    ax[0].set_ylabel('Y Coordinate')
    ax[0].grid(True)
    ax[0].legend()

    # Plot Gantt chart
    for agent, path in agent_paths.items():
        for step_index in range(len(path) - 1):
            start_time = schedule[agent][step_index]
            end_time = start_time + 1  # Each step takes 1 time unit
            ax[1].barh(f"Agent {agent}", end_time - start_time, left=start_time, color=f"C{agent}", edgecolor='black')
    
    ax[1].set_title('Gantt Chart of Agent Paths')
    ax[1].set_xlabel('Time')
    ax[1].set_ylabel('Agents')
    ax[1].grid(True)

    plt.tight_layout()
    plt.show()

def display_animated_agent_moves(agent_paths, schedule):
    """
    Display animated moves of agents on a grid.
    This function uses matplotlib to animate the moves of agents.
    """

    fig, ax = plt.subplots(figsize=(len(agent_paths) * 2, len(agent_paths) * 2))
    
    # Define a list of colors for agents
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']

    # Plot the entire path for each agent in its assigned color
    for agent, path in agent_paths.items():
        x, y = zip(*path)
        ax.plot(x, y, linestyle='--', color=colors[agent % len(colors)], label=f'Agent {agent}')

    # Create a scatter plot for the moving dots
    scat = ax.scatter([], [], s=100)

    def init():
        ax.set_xlim(-1, 5)
        ax.set_ylim(-1, 5)
        ax.legend()
        return scat,

    def update(frame):
        x_data = []
        y_data = []
        color_data = []
        for agent, path in agent_paths.items():
            if frame < len(schedule[agent]):
                x_data.append(path[frame][0])
                y_data.append(path[frame][1])
                color_data.append(colors[agent % len(colors)])  # Assign color based on agent ID
        scat.set_offsets(list(zip(x_data, y_data)))
        scat.set_color(color_data)  # Update colors for each agent
        return scat,

    ani = FuncAnimation(fig, update, frames=max(len(schedule[agent]) for agent in schedule),
                        init_func=init, blit=True, interval=1000)
    
    plt.show()

from colorama import Fore, Style

def print_grid_with_paths(grid, agent_paths):
    """
    Print the grid with paths of agents.
    """
    grid_copy = [row[:] for row in grid]  # Create a copy of the grid
    for agent, path in agent_paths.items():
        for (x, y) in path:
            # a different color for each agent
            grid_copy[x][y] = Fore.RED + str(agent) + Style.RESET_ALL  # Mark the path with agent ID
            if grid_copy[x][y] == '#':
                grid_copy[x][y] = Fore.YELLOW + '#' + Style.RESET_ALL
            else:
                grid_copy[x][y] = Fore.GREEN + str(agent) + Style.RESET_ALL

    
    for row in grid_copy:
        print(" ".join(str(cell) for cell in row))

def scenario_1():
    """
    Example scenario 1:
    20x20 Warehouse grid with 2 robots and 2 tasks (no collision).
    """
    grid = Grid(15, 15, pattern='PH2', nb_robots=2)
    robot_1 = Robot(0, 0, base_station=(19, 19))
    robot_2 = Robot(0, 1, base_station=(19, 19))

    grid.place_robot(robot_1.current_position[0], robot_1.current_position[1], robot_1)
    grid.place_robot(robot_2.current_position[0], robot_2.current_position[1], robot_2)

    # Define tasks with their target positions
    task_1 = Task("Task 1", 5, 4, 4, id=0)
    task_2 = Task("Task 2", 3, 9,9,id=1)
    grid.place_task(task_1.target[0], task_1.target[1], task_1)
    grid.place_task(task_2.target[0], task_2.target[1], task_2)

    robot_1.set_task(task_1)
    robot_2.set_task(task_2)

    print("Initial grid:")
    grid.print_grid()

    path1 = robot_1.path_to_task(grid)
    path2 = robot_2.path_to_task(grid)
    print(f"Robot 1 path to task: {path1}")
    print(f"Robot 2 path to task: {path2}")

    # Create a dictionary of agent paths
    agent_paths = {
        0: path1,
        1: path2
    }
    # Call the function to solve the multi-agent pathfinding problem
    schedule = multi_agent_pathfinding(agent_paths)
    # Print the grid with paths

def scenario_2():
    """
    Example scenario 2:
    20x20 Warehouse grid with 2 robots and 2 tasks considering time constraints.
    """
    grid = Grid(15, 15, pattern='PH', nb_robots=2)
    robot_1 = Robot(0, 0, max_energy=10, base_station=(0, 0))
    robot_2 = Robot(0, 1, base_station=(0, 0))
    robot_3 = Robot(0, 2, base_station=(0, 0))
    grid.place_robot(robot_1.current_position[0], robot_1.current_position[1], robot_1)
    grid.place_robot(robot_2.current_position[0], robot_2.current_position[1], robot_2)
    grid.place_robot(robot_3.current_position[0], robot_3.current_position[1], robot_3)
    # Define tasks with their target positions
    task_1 = Task("Task 1", 5, 4, 4, id=0)
    task_2 = Task("Task 2", 3, 9, 9, id=1)
    task_3 = Task("Task 3", 3, 12, 2, id=2)
    grid.place_task(task_1.target[0], task_1.target[1], task_1)
    grid.place_task(task_2.target[0], task_2.target[1], task_2)
    grid.place_task(task_3.target[0], task_3.target[1], task_3)
    robot_1.set_task(task_1)
    robot_2.set_task(task_2)
    robot_3.set_task(task_3)
    print("Initial grid:")
    grid.print_grid()
    path1 = robot_1.path_to_task(grid)
    path2 = robot_2.path_to_task(grid)
    path3 = robot_3.path_to_task(grid)
    print(f"Robot 1 path to task: {path1}")
    print(f"Robot 2 path to task: {path2}")
    print(f"Robot 3 path to task: {path3}")
    # Create a dictionary of agent paths
    agent_paths = {
        0: path1,
        1: path2,
        2: path3
    }
    # Call the function to solve the multi-agent pathfinding problem
    schedule = multi_agent_pathfinding(agent_paths)
    # Print the grid with paths
    print("Grid with paths:")
    print_grid_with_paths(grid.grid, agent_paths)


    robots = [robot_1, robot_2, robot_3]
    tasks = [task_1, task_2, task_3]
    # Define the total time limit for the scheduling
    total_time_limit = 10
    schedule = solve_robot_task_scheduling(robots, tasks, total_time_limit)

def scenario_3():
        # Example Usage
    agent_paths = {
        0: [(0, 0), (1, 0), (2, 0)],  # Agent 0's path
        1: [(2, 2), (2, 1), (2, 0)],  # Agent 1's path
    }
    initial_energies = {
        0: 100,  # Agent 0 starts with 5 energy
        1: 100, # Agent 1 starts with 10 energy
    }
    energy_per_step = 2  # Each step consumes 2 energy
    total_time_limit = 10

    schedule = multi_agent_pathfinding_with_energy_time(agent_paths, initial_energies, energy_per_step, total_time_limit)

if __name__ == "__main__":
    # EXAMPLE USAGE:
    # Suppose you have a 20x20 grid, and two agents with known paths.
    # Format: agent_id -> list of (x, y) cells in the path
    # grid = [[0 for _ in range(20)] for _ in range(20)]
    # # randomly add some obstacles
    # import random
    # for _ in range(50):
    #     x = random.randint(0, 19)
    #     y = random.randint(0, 19)
    #     grid[x][y] = '#'  # Mark as obstacle

    # path_0 = a_star_pathfinding((0, 0), (4, 4), grid)
    # path_1 = a_star_pathfinding((0, 0), (15, 15), grid)

    # agent_paths_example_1 = {
    #     0: path_0,
    #     1: path_1
    # }
    # # Print the paths
    # print("Agent paths:")
    # for agent, path in agent_paths_example_1.items():
    #     print(f"Agent {agent}: {path}")
    # # Call the function to solve the multi-agent pathfinding problem
    # schedule = multi_agent_pathfinding(agent_paths_example_1)
    # # Print the grid with paths
    # print("Grid with paths:")
    # print_grid_with_paths(grid, agent_paths_example_1)

    scenario_2()

    # if schedule:
    #     # Plot the paths and Gantt chart
    #     plot_paths_and_gantt(agent_paths_example_1, schedule)
        
    #     # Display animated moves of agents
    #     display_animated_agent_moves(agent_paths_example_1, schedule)
    # You can also visualize the paths separately