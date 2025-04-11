"""
Modèle de base pour le problème de Job-Shop Scheduling
utilisant la programmation par contraintes avec Google OR-Tools.
"""

from ortools.sat.python import cp_model
import time
from instances.instance_small import small_instance
from visualization import visualize_schedule, print_solution

def solve_jobshop(jobs_data, time_limit=60):
    """
    Résout un problème de Job-Shop Scheduling en utilisant CP-SAT solver.
    
    Args:
        jobs_data: Liste de jobs, où chaque job est une liste d'opérations.
                  Chaque opération est un tuple (machine_id, processing_time).
        time_limit: Limite de temps pour la résolution en secondes.
        
    Returns:
        tuple: (instance, all_tasks, makespan) où:
               - instance est le dictionnaire des données du problème
               - all_tasks est un dictionnaire des tâches planifiées
               - makespan est la durée totale de la planification
    """
    # Données du problème
    num_jobs = len(jobs_data)
    all_jobs = range(num_jobs)
    
    # Déterminer le nombre de machines
    num_machines = 0
    for job in jobs_data:
        for op in job:
            num_machines = max(num_machines, op[0] + 1)
    all_machines = range(num_machines)
    
    # Calcul de l'horizon (borne supérieure de la durée totale)
    horizon = sum(op[1] for job in jobs_data for op in job)
    
    # Création du modèle
    model = cp_model.CpModel()
    
    # Variables d'intervalle pour chaque opération
    all_tasks = {}
    machine_to_intervals = {m: [] for m in all_machines}
    
    # Variables pour les temps de début/fin de chaque opération
    task_starts = {}
    task_ends = {}
    
    # Pour chaque job et chaque opération dans le job
    for job_id in all_jobs:
        job = jobs_data[job_id]
        for op_id, operation in enumerate(job):
            machine, processing_time = operation
            
            # Créer des variables pour le début et la fin de l'opération
            # Le temps de début est entre 0 et horizon - processing_time
            start_var = model.NewIntVar(0, horizon - processing_time, 
                                        f'start_job{job_id}_op{op_id}')
            end_var = model.NewIntVar(processing_time, horizon, 
                                     f'end_job{job_id}_op{op_id}')
            
            # Créer une variable d'intervalle pour cette opération
            interval_var = model.NewIntervalVar(start_var, processing_time, end_var,
                                              f'interval_job{job_id}_op{op_id}')
            
            # Enregistrer les variables pour une utilisation ultérieure
            all_tasks[(job_id, op_id)] = (start_var, end_var, interval_var)
            task_starts[(job_id, op_id)] = start_var
            task_ends[(job_id, op_id)] = end_var
            
            # Ajouter cette opération à la liste des opérations de cette machine
            machine_to_intervals[machine].append(interval_var)
    
    # Contrainte 1: Les opérations ne peuvent pas se chevaucher sur une même machine
    for machine in all_machines:
        model.AddNoOverlap(machine_to_intervals[machine])
    
    # Contrainte 2: Respecter l'ordre des opérations dans chaque job
    for job_id in all_jobs:
        for op_id in range(len(jobs_data[job_id]) - 1):
            # L'opération suivante ne peut commencer qu'après la fin de l'opération actuelle
            model.Add(task_starts[(job_id, op_id + 1)] >= task_ends[(job_id, op_id)])
    
    # Objectif: Minimiser le makespan (temps total)
    # Le makespan est le maximum des temps de fin de toutes les opérations
    makespan_var = model.NewIntVar(0, horizon, 'makespan')
    all_ends = [task_ends[(job_id, len(jobs_data[job_id]) - 1)] for job_id in all_jobs]
    model.AddMaxEquality(makespan_var, all_ends)
    model.Minimize(makespan_var)
    
    # Résolution du modèle
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    
    start_time = time.time()
    status = solver.Solve(model)
    solve_time = time.time() - start_time
    
    # Vérification de la solution
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"Solution {'optimale' if status == cp_model.OPTIMAL else 'réalisable'} trouvée en {solve_time:.2f} secondes.")
        
        # Extraire les valeurs des variables pour le makespan et les tâches
        makespan = solver.Value(makespan_var)
        
        # Préparer les résultats
        assignments = {}
        for (job_id, op_id), (start_var, end_var, _) in all_tasks.items():
            machine = jobs_data[job_id][op_id][0]
            start_time = solver.Value(start_var)
            end_time = solver.Value(end_var)
            assignments[(job_id, op_id)] = (start_time, end_time, machine)
        
        # Données d'instance formatées pour la visualisation
        instance = {
            'jobs_data': jobs_data,
            'num_jobs': num_jobs,
            'num_machines': num_machines,
            'horizon': horizon
        }
        
        return instance, assignments, makespan
    else:
        print("Aucune solution trouvée dans le temps imparti.")
        return None, None, None

def main():
    """Fonction principale pour exécuter le solveur avec l'instance par défaut."""
    jobs_data = small_instance()
    instance, assignments, makespan = solve_jobshop(jobs_data)
    
    if assignments:
        print(f"Makespan: {makespan}")
        print_solution(assignments, instance['num_jobs'], instance['num_machines'])
        visualize_schedule(instance, assignments)

if __name__ == '__main__':
    main()