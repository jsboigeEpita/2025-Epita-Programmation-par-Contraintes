from entities.stadium import Stadium
from entities.team import Team
from entities.scheduler import Schedule
from utils.utils import solve_schedule
import time
import pandas as pd

def benchmark_ortools(team_sizes, start_date="2025-04-01", max_consecutive_away=2):
    results = []

    for n in team_sizes:
        print(f"\nBenchmarking for {n} teams...")

        stadiums = [Stadium(f"Stadium {i+1}") for i in range(n)]
        teams = [Team(f"Team {chr(65+i)}", stadiums[i]) for i in range(n)]

        start_time = time.time()
        schedule = Schedule(teams, start_date=start_date, max_consecutive_away=max_consecutive_away)
        end_time = time.time()

        duration = end_time - start_time
        status = "Feasible" if schedule.schedule else "Infeasible"

        results.append({
            "num_teams": n,
            "solve_time_sec": round(duration, 3),
            "status": status,
            "total_breaks": schedule.total_breaks_value if schedule.schedule else None
        })

    return pd.DataFrame(results)

# --- MAIN ---
if __name__ == "__main__":
    team_sizes = [6, 8, 10, 12, 14, 16, 18, 20]
    df = benchmark_ortools(team_sizes)
    print("\n--- OR-Tools Benchmark Results ---")
    print(df.to_markdown(index=False))

    with open("result.output") as f:
        f.write(df.to_markdown(index=False))