from flask import Flask, request, jsonify
# Il faut vous assurer que le fichier robots-ortools-3.py est renommé ou accessible en tant que module.
# Par exemple, ici on suppose que le fichier est disponible en tant que module "robots_ortools_3".
from robots_ortools_3 import Grid, Robot, Task, multi_agent_pathfinding, solve_robot_task_scheduling

app = Flask(__name__)

@app.route("/simulate", methods=["POST"])
def simulate():
    """
    Attend en POST un objet JSON de la forme :
    
      {
          "gridSize": 15,
          "robotCount": 2,
          "tasks": [
              { "xEnd": 4, "yEnd": 4 },
              { "xEnd": 9, "yEnd": 9 }
          ],
          "timeLimit": 10
      }
    
    La simulation consiste à :
      1. Créer une grille de dimension gridSize x gridSize.
      2. Créer robotCount robots que l’on place sur la grille (ici, on les positionne sur la première ligne,
         en décalant la colonne pour éviter les collisions).
      3. Pour chaque tâche reçue (contenant xEnd et yEnd) on crée un objet Task et on le place sur la grille.
      4. On assigne à chaque robot (dans l’ordre) une tâche parmi celles qui ont été définies.
      5. Pour chaque robot possédant une tâche, on calcule le chemin jusqu’à la position cible avec la fonction a_star.
    
    La réponse renvoyée est un dictionnaire associant l’identifiant du robot à la liste des coordonnées (le chemin).
    """
    data = request.get_json()

    # Récupération des paramètres d'initialisation
    grid_size = data.get("gridSize")
    robot_count = data.get("robotCount")
    tasks_data = data.get("tasks")
    time_limit = data.get("timeLimit")  # Limite de temps pour la recherche de chemin
    
    print(f"Grid Size: {grid_size}, Robot Count: {robot_count}, Tasks: {tasks_data}, Time Limit: {time_limit}")

    # Création de la grille (ici on choisit le pattern 'PH2', mais vous pouvez le modifier)
    grid = Grid(grid_size, grid_size, pattern="PH2", nb_robots=robot_count)
    
    # Création des robots. Nous les plaçons sur la première ligne, de la colonne 0 à robot_count-1
    robots = []
    for i in range(robot_count):
        # On initialise chaque robot à la position (0, i)
        robot = Robot(0, i)
        grid.place_robot(0, i, robot)
        robots.append(robot)
    
    # Création des tâches et placement sur la grille
    tasks = []
    for idx, task_in in enumerate(tasks_data):
        # On crée une tâche avec un nom et une durée par défaut (ici, 1)
        # Les coordonnées cibles sont fournies dans xEnd et yEnd
        task = Task(name=f"Task {idx}", time=1, target_x=task_in["xEnd"], target_y=task_in["yEnd"], id=idx)
        tasks.append(task)
    # Calculer l'association robot-tâche avec la méthode solve_robot_task_scheduling
    task_attribution_csp = solve_robot_task_scheduling(robots, tasks, time_limit)
    
    
    # On assigne les tâches aux robots
    for robot, task in zip(robots, tasks):
        # On assigne la tâche au robot
        robot.set_task(task)
        # On place la tâche sur la grille
        grid.place_task(task.target[0], task.target[1], task)


    # Pour chaque robot ayant une tâche, on calcule le chemin avec la méthode path_to_task
    # La méthode utilise l'algorithme A* défini dans le fichier pour chercher le chemin le plus court.
    robot_paths = {}
    for robot in robots:
        if robot.task is not None:
            path = robot.path_to_task(grid)
            # Le chemin sera une liste de tuples (x, y) indiquant la trajectoire
            robot_paths[robot.id] = path
        else:
            robot_paths[robot.id] = []
    
    path_schedule = multi_agent_pathfinding(robot_paths)
    # Retourner une réponse JSON contenant l'association robot_id -> chemin

    # Make task_attribution_csp and path_schedule json
    # Convert task_attribution_csp to a JSON-serializable format
        # Convert task_attribution_csp to a JSON-serializable format
    task_attribution_csp_serializable = {
        robot_id: [
            {
                "id": t[0].id if isinstance(t, tuple) else t.id,
                "name": t[0].name if isinstance(t, tuple) else t.name,
                "duration": t[0].duration if isinstance(t, tuple) else t.duration,
                "target": t[0].target if isinstance(t, tuple) else t.target,
                "energy_cost": t[0].energy_cost if isinstance(t, tuple) else t.energy_cost
            }
            for t in task  # Iterate over the list of tasks if task is a list
        ] if isinstance(task, list) else {
            "id": task[0].id if isinstance(task, tuple) else task.id,
            "name": task[0].name if isinstance(task, tuple) else task.name,
            "duration": task[0].duration if isinstance(task, tuple) else task.duration,
            "target": task[0].target if isinstance(task, tuple) else task.target,
            "energy_cost": task[0].energy_cost if isinstance(task, tuple) else task.energy_cost
        }
        for robot_id, task in task_attribution_csp.items()
    }


    # Convert robot_paths to a JSON-serializable format
    robot_paths_serializable = {
        robot_id: path for robot_id, path in robot_paths.items()
    }
    
    print(path_schedule)
    return jsonify({"path_schedule": path_schedule, "task_schedule": task_attribution_csp_serializable, "path_schedule": robot_paths_serializable})

if __name__ == "__main__":
    app.run(debug=True)