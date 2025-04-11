"""
Instance de petite taille pour le problème de Job-Shop Scheduling.
Cette instance contient 3 jobs et 3 machines.
"""

def small_instance():
    """
    Retourne une petite instance du problème de Job-Shop.
    
    Format: Liste de jobs, où chaque job est une liste d'opérations.
           Chaque opération est un tuple (machine_id, processing_time).
    
    Returns:
        list: Données de l'instance
    """
    jobs_data = [
        # Job 0: 3 opérations
        [
            (0, 3),  # (machine 0, processing_time 3)
            (1, 4),  # (machine 1, processing_time 4)
            (2, 2),  # (machine 2, processing_time 2)
        ],
        # Job 1: 3 opérations
        [
            (0, 2),  # (machine 0, processing_time 2)
            (2, 3),  # (machine 2, processing_time 3)
            (1, 3),  # (machine 1, processing_time 3)
        ],
        # Job 2: 3 opérations
        [
            (1, 2),  # (machine 1, processing_time 2)
            (2, 4),  # (machine 2, processing_time 4)
            (0, 3),  # (machine 0, processing_time 3)
        ],
    ]
    
    return jobs_data