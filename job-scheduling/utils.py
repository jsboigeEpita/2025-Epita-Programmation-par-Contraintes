"""
Fonctions utilitaires pour le problème de Job-Shop Scheduling.
"""

def export_solution_to_csv(instance, assignments, filename):
    """
    Exporte la solution vers un fichier CSV.
    
    Args:
        instance: Dictionnaire des données du problème
        assignments: Dictionnaire des tâches planifiées
                    {(job_id, op_id): (start_time, end_time, machine_id)}
        filename: Nom du fichier CSV de sortie
    """
    import csv
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Job', 'Operation', 'Machine', 'Start', 'End', 'Duration'])
        
        # Trier les opérations par job, puis par opération
        sorted_assignments = sorted(assignments.items())
        
        for (job_id, op_id), (start, end, machine) in sorted_assignments:
            duration = end - start
            writer.writerow([job_id, op_id, machine, start, end, duration])

def calculate_metrics(instance, assignments):
    """
    Calcule différentes métriques de performance pour la solution.
    
    Args:
        instance: Dictionnaire des données du problème
        assignments: Dictionnaire des tâches planifiées
        
    Returns:
        dict: Métriques de performance
    """
    # Makespan (temps total)
    makespan = max(end for _, (_, end, _) in assignments.items())
    
    # Temps d'inactivité des machines
    idle_times = {}
    machine_to_ops = {}
    
    for (job_id, op_id), (start, end, machine) in assignments.items():
        if machine not in machine_to_ops:
            machine_to_ops[machine] = []
        machine_to_ops[machine].append((start, end))
    
    for machine, ops in machine_to_ops.items():
        # Trier les opérations par temps de début
        ops.sort()
        
        # Calculer le temps d'inactivité
        idle_time = 0
        current_time = 0
        
        for start, end in ops:
            if start > current_time:
                idle_time += start - current_time
            current_time = max(current_time, end)
        
        idle_times[machine] = idle_time
    
    total_idle_time = sum(idle_times.values())
    
    # Temps de complétion moyen des jobs
    job_completion_times = {}
    for (job_id, op_id), (start, end, _) in assignments.items():
        if job_id not in job_completion_times:
            job_completion_times[job_id] = 0
        job_completion_times[job_id] = max(job_completion_times[job_id], end)
    
    avg_completion_time = sum(job_completion_times.values()) / len(job_completion_times)
    
    # Flow time (temps passé dans le système) pour chaque job
    job_start_times = {}
    for (job_id, op_id), (start, end, _) in assignments.items():
        if job_id not in job_start_times:
            job_start_times[job_id] = float('inf')
        job_start_times[job_id] = min(job_start_times[job_id], start)
    
    flow_times = {job_id: job_completion_times[job_id] - job_start_times[job_id] 
                for job_id in job_completion_times}
    avg_flow_time = sum(flow_times.values()) / len(flow_times)
    
    # Retards si des dates d'échéance sont spécifiées
    tardiness = 0
    if 'due_dates' in instance and instance['due_dates']:
        due_dates = instance['due_dates']
        for job_id, completion_time in job_completion_times.items():
            if job_id in due_dates:
                tardiness += max(0, completion_time - due_dates[job_id])
    
    # Calculer l'utilisation des machines
    machine_utilization = {}
    for machine, ops in machine_to_ops.items():
        total_processing_time = sum(end - start for start, end in ops)
        machine_utilization[machine] = total_processing_time / makespan
    
    avg_machine_utilization = sum(machine_utilization.values()) / len(machine_utilization)
    
    # Rassembler toutes les métriques
    metrics = {
        'makespan': makespan,
        'total_idle_time': total_idle_time,
        'avg_completion_time': avg_completion_time,
        'avg_flow_time': avg_flow_time,
        'tardiness': tardiness,
        'avg_machine_utilization': avg_machine_utilization
    }
    
    return metrics

def compare_solutions(solution1, solution2):
    """
    Compare deux solutions et affiche les différences.
    
    Args:
        solution1: Tuple (instance1, assignments1, metrics1)
        solution2: Tuple (instance2, assignments2, metrics2)
    """
    _, assignments1, metrics1 = solution1
    _, assignments2, metrics2 = solution2
    
    print("Comparaison des solutions:")
    print(f"Makespan: {metrics1['makespan']} vs {metrics2['makespan']} " + 
          f"({metrics1['makespan'] - metrics2['makespan']})")
    
    print(f"Temps d'inactivité: {metrics1['total_idle_time']} vs {metrics2['total_idle_time']} " + 
          f"({metrics1['total_idle_time'] - metrics2['total_idle_time']})")
    
    print(f"Temps de complétion moyen: {metrics1['avg_completion_time']:.2f} vs {metrics2['avg_completion_time']:.2f} " + 
          f"({metrics1['avg_completion_time'] - metrics2['avg_completion_time']:.2f})")
    
    print(f"Retard: {metrics1['tardiness']} vs {metrics2['tardiness']} " + 
          f"({metrics1['tardiness'] - metrics2['tardiness']})")
    
    print(f"Utilisation moyenne des machines: {metrics1['avg_machine_utilization']:.2%} vs " + 
          f"{metrics2['avg_machine_utilization']:.2%} " + 
          f"({metrics1['avg_machine_utilization'] - metrics2['avg_machine_utilization']:.2%})")
    
    # Identifier les différences dans l'affectation des opérations
    diff_assignments = []
    for key in assignments1:
        if key in assignments2:
            if assignments1[key] != assignments2[key]:
                diff_assignments.append((key, assignments1[key], assignments2[key]))
    
    if diff_assignments:
        print("\nDifférences d'affectation:")
        for (job_id, op_id), assign1, assign2 in diff_assignments:
            print(f"Job {job_id}, Op {op_id}: {assign1} vs {assign2}")