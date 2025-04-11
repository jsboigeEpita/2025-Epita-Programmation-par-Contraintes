"""
Instance de grande taille pour le problème de Job-Shop Scheduling.
Cette instance contient 15 jobs et 10 machines.
"""

import random

def generate_large_instance(seed=42):
    """
    Génère une instance aléatoire de grande taille du problème de Job-Shop.
    
    Format: Liste de jobs, où chaque job est une liste d'opérations.
           Chaque opération est un tuple (machine_id, processing_time).
    
    Args:
        seed: Graine pour le générateur de nombres aléatoires
        
    Returns:
        list: Données de l'instance
    """
    random.seed(seed)
    
    num_jobs = 15
    num_machines = 10
    min_time = 2
    max_time = 10
    
    jobs_data = []
    
    for _ in range(num_jobs):
        # Créer une liste d'opérations pour ce job
        job = []
        
        # Déterminer un ordre aléatoire des machines pour ce job
        machines = list(range(num_machines))
        random.shuffle(machines)
        
        for machine in machines:
            # Déterminer un temps de traitement aléatoire pour cette opération
            processing_time = random.randint(min_time, max_time)
            job.append((machine, processing_time))
        
        jobs_data.append(job)
    
    return jobs_data

def large_instance():
    """
    Retourne une grande instance pré-générée du problème de Job-Shop.
    
    Returns:
        list: Données de l'instance
    """
    # Utiliser une graine fixe pour la reproductibilité
    return generate_large_instance(seed=42)