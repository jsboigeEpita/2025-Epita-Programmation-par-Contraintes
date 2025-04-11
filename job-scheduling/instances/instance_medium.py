"""
Instance de taille moyenne pour le problème de Job-Shop Scheduling.
Cette instance contient 10 jobs et 5 machines.
"""

def medium_instance():
    """
    Retourne une instance moyenne du problème de Job-Shop.
    
    Format: Liste de jobs, où chaque job est une liste d'opérations.
           Chaque opération est un tuple (machine_id, processing_time).
    
    Returns:
        list: Données de l'instance
    """
    jobs_data = [
        # Job 0
        [
            (0, 5),   # (machine 0, processing_time 5)
            (1, 4),   # (machine 1, processing_time 4)
            (2, 7),   # (machine 2, processing_time 7)
            (3, 2),   # (machine 3, processing_time 2)
            (4, 3),   # (machine 4, processing_time 3)
        ],
        # Job 1
        [
            (1, 6),   # (machine 1, processing_time 6)
            (0, 3),   # (machine 0, processing_time 3)
            (2, 5),   # (machine 2, processing_time 5)
            (4, 4),   # (machine 4, processing_time 4)
            (3, 2),   # (machine 3, processing_time 2)
        ],
        # Job 2
        [
            (2, 4),   # (machine 2, processing_time 4)
            (3, 5),   # (machine 3, processing_time 5)
            (0, 6),   # (machine 0, processing_time 6)
            (1, 2),   # (machine 1, processing_time 2)
            (4, 3),   # (machine 4, processing_time 3)
        ],
        # Job 3
        [
            (3, 3),   # (machine 3, processing_time 3)
            (2, 5),   # (machine 2, processing_time 5)
            (4, 4),   # (machine 4, processing_time 4)
            (1, 6),   # (machine 1, processing_time 6)
            (0, 2),   # (machine 0, processing_time 2)
        ],
        # Job 4
        [
            (4, 5),   # (machine 4, processing_time 5)
            (3, 4),   # (machine 3, processing_time 4)
            (2, 3),   # (machine 2, processing_time 3)
            (0, 5),   # (machine 0, processing_time 5)
            (1, 4),   # (machine 1, processing_time 4)
        ],
        # Job 5
        [
            (1, 5),   # (machine 1, processing_time 5)
            (0, 7),   # (machine 0, processing_time 7)
            (4, 2),   # (machine 4, processing_time 2)
            (3, 6),   # (machine 3, processing_time 6)
            (2, 3),   # (machine 2, processing_time 3)
        ],
        # Job 6
        [
            (0, 4),   # (machine 0, processing_time 4)
            (2, 6),   # (machine 2, processing_time 6)
            (1, 3),   # (machine 1, processing_time 3)
            (4, 5),   # (machine 4, processing_time 5)
            (3, 2),   # (machine 3, processing_time 2)
        ],
        # Job 7
        [
            (2, 5),   # (machine 2, processing_time 5)
            (1, 4),   # (machine 1, processing_time 4)
            (0, 3),   # (machine 0, processing_time 3)
            (3, 7),   # (machine 3, processing_time 7)
            (4, 5),   # (machine 4, processing_time 5)
        ],
        # Job 8
        [
            (4, 6),   # (machine 4, processing_time 6)
            (3, 3),   # (machine 3, processing_time 3)
            (2, 4),   # (machine 2, processing_time 4)
            (1, 5),   # (machine 1, processing_time 5)
            (0, 2),   # (machine 0, processing_time 2)
        ],
        # Job 9
        [
            (3, 4),   # (machine 3, processing_time 4)
            (0, 5),   # (machine 0, processing_time 5)
            (1, 3),   # (machine 1, processing_time 3)
            (2, 6),   # (machine 2, processing_time 6)
            (4, 2),   # (machine 4, processing_time 2)
        ],
    ]
    
    return jobs_data