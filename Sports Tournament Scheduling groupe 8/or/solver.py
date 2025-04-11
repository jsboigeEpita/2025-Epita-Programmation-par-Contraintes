from ortools.sat.python import cp_model
from datetime import datetime, timedelta
from entities.stadium import Stadium
from entities.team import Team
from entities.scheduler import Schedule
from utils.utils import solve_schedule

# Exemple d'utilisation
if __name__ == "__main__":
    nb_teams = 4
    start_date="2025-04-01"
    max_consecutive_away = 2
    result = solve_schedule(nb_teams,start_date,2)
    print(result)
