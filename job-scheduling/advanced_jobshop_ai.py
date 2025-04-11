"""
Modèle avancé pour le problème de Job-Shop Scheduling
avec des contraintes supplémentaires et amélioration par AI.
"""

from ortools.sat.python import cp_model
import time
from instances.instance_medium import medium_instance
from instances.instance_small import small_instance
from instances.instance_large import large_instance
from visualization import visualize_advanced_schedule, print_solution
# Import the new AI enhancer module
from ai_enhancer import get_ai_parameter_suggestions, analyze_solution, explain_schedule

def solve_advanced_jobshop(jobs_data, maintenance_periods=None, due_dates=None, 
                         setup_times=None, resource_capacity=None, 
                         resource_usage=None, time_limit=120,
                         makespan_weight=1, tardiness_weight=1000):
    """
    Résout un problème avancé de Job-Shop Scheduling avec contraintes supplémentaires.
    
    Args:
        jobs_data: Liste de jobs, où chaque job est une liste d'opérations.
                  Chaque opération est un tuple (machine_id, processing_time).
        maintenance_periods: Liste de périodes de maintenance.
                            Chaque période est un tuple (machine_id, start_time, duration).
        due_dates: Dictionnaire des dates d'échéance par job {job_id: due_date}.
        setup_times: Matrice des temps de préparation dépendants de la séquence.
                    setup_times[prev_job_id][next_job_id][machine_id] = setup_time.
        resource_capacity: Capacité maximale des ressources cumulatives (énergie, personnel).
        resource_usage: Consommation de ressources par opération.
                      resource_usage[(job_id, op_id)] = resource_amount.
        time_limit: Limite de temps pour la résolution en secondes.
        makespan_weight: Poids du makespan dans la fonction objectif.
        tardiness_weight: Poids du retard dans la fonction objectif.
        
    Returns:
        tuple: (instance, all_tasks, makespan, tardiness) où:
               - instance est le dictionnaire des données du problème
               - all_tasks est un dictionnaire des tâches planifiées
               - makespan est la durée totale de la planification
               - tardiness est le retard total par rapport aux dates d'échéance
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
    if maintenance_periods:
        for _, start, duration in maintenance_periods:
            horizon += duration
    if setup_times:
        # Ajouter une estimation des temps de préparation
        max_setup = max(max(max(st.values()) for st in setup.values()) for setup in setup_times.values())
        horizon += num_jobs * max_setup
        
    # Valeurs par défaut pour les paramètres optionnels
    if due_dates is None:
        due_dates = {job_id: horizon for job_id in all_jobs}
    if resource_capacity is None:
        resource_capacity = float('inf')  # Pas de limite de ressources
    if resource_usage is None:
        resource_usage = {(job_id, op_id): 1 
                         for job_id in all_jobs 
                         for op_id in range(len(jobs_data[job_id]))}
    
    # Création du modèle
    model = cp_model.CpModel()
    
    # Variables d'intervalle pour chaque opération
    all_tasks = {}
    machine_to_intervals = {m: [] for m in all_machines}
    
    # Variables pour les temps de début/fin de chaque opération
    task_starts = {}
    task_ends = {}
    
    # Variables pour les opérations précédentes/suivantes sur chaque machine
    # (utilisé pour les temps de préparation)
    machine_to_jobs = {m: [] for m in all_machines}
    
    # Pour chaque job et chaque opération dans le job
    for job_id in all_jobs:
        job = jobs_data[job_id]
        for op_id, operation in enumerate(job):
            machine, processing_time = operation
            
            # Créer des variables pour le début et la fin de l'opération
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
            machine_to_jobs[machine].append(job_id)

    # Ajouter les périodes de maintenance
    if maintenance_periods:
        for machine_id, start_time, duration in maintenance_periods:
            # Créer une variable d'intervalle fixe pour la période de maintenance
            maintenance_start = model.NewConstant(start_time)
            maintenance_end = model.NewConstant(start_time + duration)
            maintenance_interval = model.NewIntervalVar(
                maintenance_start, duration, maintenance_end,
                f'maintenance_machine{machine_id}_at_{start_time}'
            )
            # Ajouter cette période aux contraintes de non-chevauchement de la machine
            machine_to_intervals[machine_id].append(maintenance_interval)
    
    # Contrainte 1 et 3: Les opérations ne peuvent pas se chevaucher sur une même machine (maintenance incluse)
    for machine in all_machines:
        model.AddNoOverlap(machine_to_intervals[machine])
    
    # Contrainte 2: Respecter l'ordre des opérations dans chaque job
    for job_id in all_jobs:
        for op_id in range(len(jobs_data[job_id]) - 1):
            # L'opération suivante ne peut commencer qu'après la fin de l'opération actuelle
            model.Add(task_starts[(job_id, op_id + 1)] >= task_ends[(job_id, op_id)])

    
    # Contrainte 4: Temps de préparation dépendant de la séquence
    if setup_times:
        for machine in all_machines:
            jobs_on_machine = [(job_id, op_id) for job_id in all_jobs 
                            for op_id in range(len(jobs_data[job_id])) 
                            if jobs_data[job_id][op_id][0] == machine]
            
            # Si la machine ne traite qu'une seule opération ou aucune, 
            # pas besoin de contraintes de setup
            if len(jobs_on_machine) <= 1:
                continue
            
            # Pour chaque paire d'opérations sur cette machine
            for i, (job_id1, op_id1) in enumerate(jobs_on_machine):
                for j, (job_id2, op_id2) in enumerate(jobs_on_machine):
                    if i == j:
                        continue
                    
                    # Temps de préparation pour passer du job1 au job2 sur cette machine
                    setup_time = setup_times.get(job_id1, {}).get(job_id2, {}).get(machine, 0)
                    
                    # Créer une variable booléenne indiquant si job2 suit job1 (pas nécessairement directement)
                    job2_after_job1 = model.NewBoolVar(f'job{job_id2}_op{op_id2}_after_job{job_id1}_op{op_id1}')
                    
                    # Si job2_after_job1 est vrai, alors job2 commence après la fin de job1 + temps de setup
                    model.Add(task_starts[(job_id2, op_id2)] >= 
                            task_ends[(job_id1, op_id1)] + setup_time).OnlyEnforceIf(job2_after_job1)
                    
                    # Si job2_after_job1 est faux, alors job1 commence après la fin de job2
                    # (pas besoin d'ajouter le temps de setup dans ce cas car c'est une autre variable qui le gèrera)
                    model.Add(task_starts[(job_id1, op_id1)] >= 
                            task_ends[(job_id2, op_id2)]).OnlyEnforceIf(job2_after_job1.Not())
    
    # Contrainte 5: Ressources cumulatives (énergie, personnel)
    if resource_capacity < float('inf'):
        # Utiliser une approche basée sur les intervalles (beaucoup plus efficace)
        resource_intervals = []
        resource_demands = []
        
        for job_id in all_jobs:
            for op_id in range(len(jobs_data[job_id])):
                # Récupérer l'utilisation de ressource pour cette opération
                usage = resource_usage.get((job_id, op_id), 0)
                if usage > 0:
                    # Utiliser l'intervalle existant et indiquer sa demande en ressource
                    interval_var = all_tasks[(job_id, op_id)][2]  # Récupérer l'IntervalVar
                    resource_intervals.append(interval_var)
                    resource_demands.append(usage)
    
    # Ajouter une contrainte cumulative sur toutes les opérations
    if resource_intervals:
        model.AddCumulative(resource_intervals, resource_demands, resource_capacity)
    
    # Variables pour les dates d'échéance et retards
    tardiness_vars = []
    for job_id in all_jobs:
        due_date = due_dates[job_id]
        last_op_id = len(jobs_data[job_id]) - 1
        job_end = task_ends[(job_id, last_op_id)]
        
        # Calculer le retard (max(0, job_end - due_date))
        tardiness = model.NewIntVar(0, horizon, f'tardiness_job{job_id}')
        model.AddMaxEquality(tardiness, [model.NewConstant(0), job_end - due_date])
        tardiness_vars.append(tardiness)
    
    # Objectif: Minimiser le makespan et le retard total
    makespan_var = model.NewIntVar(0, horizon, 'makespan')
    all_ends = [task_ends[(job_id, len(jobs_data[job_id]) - 1)] for job_id in all_jobs]
    model.AddMaxEquality(makespan_var, all_ends)
    
    total_tardiness = model.NewIntVar(0, horizon * num_jobs, 'total_tardiness')
    model.Add(total_tardiness == sum(tardiness_vars))
    
    # Objectif à deux critères pondérés avec les poids fournis
    # Utilise les poids qui pourraient être suggérés par l'IA
    model.Minimize(makespan_weight * makespan_var + tardiness_weight * total_tardiness)
    
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
        total_tardiness_value = solver.Value(total_tardiness)
        
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
            'maintenance_periods': maintenance_periods,
            'due_dates': due_dates,
            'num_jobs': num_jobs,
            'num_machines': num_machines,
            'horizon': horizon
        }
        
        return instance, assignments, makespan, total_tardiness_value
    else:
        print("Aucune solution trouvée dans le temps imparti.")
        return None, None, None, None

def solve_with_ai_parameters(jobs_data, maintenance_periods=None, due_dates=None, 
                           setup_times=None, resource_capacity=None, 
                           resource_usage=None, time_limit=120):
    """
    Solve the job shop problem using AI-suggested parameters.
    
    This function wraps the original solver with AI parameter suggestions.
    """
    # Create basic instance data
    num_jobs = len(jobs_data)
    num_machines = 0
    for job in jobs_data:
        for op in job:
            num_machines = max(num_machines, op[0] + 1)
    
    instance = {
        'jobs_data': jobs_data,
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'maintenance_periods': maintenance_periods,
        'due_dates': due_dates,
    }
    
    # Get AI recommendations for parameters
    print("Consulting AI for optimal parameters...")
    ai_params = get_ai_parameter_suggestions(instance)
    
    if ai_params:
        print(f"AI recommends: {ai_params}")
        makespan_weight = ai_params.get('makespan_weight', 1)
        tardiness_weight = ai_params.get('tardiness_weight', 1000)
    else:
        print("Using default parameters")
        makespan_weight = 1
        tardiness_weight = 1000
    
    # Run solver with AI-recommended parameters
    print(f"Solving with parameters: makespan_weight={makespan_weight}, tardiness_weight={tardiness_weight}")
    instance, assignments, makespan, tardiness = solve_advanced_jobshop(
        jobs_data, 
        maintenance_periods=maintenance_periods,
        due_dates=due_dates,
        setup_times=setup_times,
        resource_capacity=resource_capacity,
        resource_usage=resource_usage,
        time_limit=time_limit,
        makespan_weight=makespan_weight,
        tardiness_weight=tardiness_weight
    )
    
    return instance, assignments, makespan, tardiness

def main():
    """Fonction principale pour exécuter le solveur avec l'instance par défaut."""
    print("=== AI-Enhanced Job Shop Scheduler ===")
    
    # Préparation des données d'instance de taille moyenne
    jobs_data = large_instance()  # Vous pouvez changer pour small_instance() ou large_instance()
    
    # Périodes de maintenance pour certaines machines
    maintenance_periods = [
        (1, 0, 10),  # Machine 0 indisponible de t=20 à t=25
        (2, 40, 10)  # Machine 2 indisponible de t=40 à t=50
    ]
    
    # Dates d'échéance pour chaque job
    num_jobs = len(jobs_data)
    due_dates = {j: 80 + j * 5 for j in range(num_jobs)}  # Dates d'échéance échelonnées
    
    # Temps de préparation dépendant de la séquence (pour certaines transitions)
    setup_times = {}
    for j1 in range(num_jobs):
        setup_times[j1] = {}
        for j2 in range(num_jobs):
            if j1 != j2:
                setup_times[j1][j2] = {m: 2 for m in range(5)}  # 2 unités de temps pour chaque machine
    setup_times[0][1] = {0: 7, 1: 7}  # Temps de setup spécifique pour la transition entre job 0 et job 1
    setup_times[1][0] = {0: 7, 1: 7}  # Temps de setup spécifique pour la transition entre job 0 et job 1
    
    # Capacité et consommation de ressources
    resource_capacity = 5  # Maximum 3 opérations simultanées
    resource_usage = {}
    for j in range(num_jobs):
        for op in range(len(jobs_data[j])):
            resource_usage[(j, op)] = 1  # Chaque opération utilise 1 unité de ressource
    
    # Résoudre le problème avec paramètres suggérés par l'IA
    print("=== Solving with AI parameters ===")
    instance, assignments, makespan, tardiness = solve_with_ai_parameters(
        jobs_data, 
        maintenance_periods=maintenance_periods,
        due_dates=due_dates,
        setup_times=setup_times,
        resource_capacity=resource_capacity,
        resource_usage=resource_usage
    )
    
    if assignments:
        print(f"Makespan: {makespan}")
        print(f"Retard total: {tardiness}")
        print_solution(assignments, instance['num_jobs'], instance['num_machines'])
        
        # Obtenir analyse et explication de l'IA
        print("\n=== AI Analysis of Solution ===")
        ai_analysis = analyze_solution(instance, assignments, makespan, tardiness)
        print(ai_analysis)
        
        print("\n=== AI Explanation of Schedule ===")
        explanation = explain_schedule(instance, assignments, makespan, tardiness)
        print(explanation)
        
        # Visualiser le planning avec périodes de maintenance
        visualize_advanced_schedule(instance, assignments)

if __name__ == '__main__':
    main()