from entities.stadium import Stadium
from entities.team import Team
from entities.scheduler import Schedule
from datetime import datetime, timedelta

def solve_schedule(num_teams: int, start_date: str, max_consecutive_away: int) -> str:
    stadiums = [Stadium(f"Stadium {i + 1}") for i in range(num_teams)]
    teams = [Team(f"Team {chr(65 + i)}", stadiums[i]) for i in range(num_teams)]

    schedule = Schedule(teams, start_date, max_consecutive_away)

    if schedule.schedule is None:
        return "No feasible schedule found."

    output = ""
    for day, matches in enumerate(schedule.schedule, start=1):
        date_str = (schedule.start_date + timedelta(days=day - 1)).strftime("%Y-%m-%d")
        output += f"Day {day} ({date_str}):\n"
        for home, away in matches:
            output += f"  {teams[home].name} (home) vs {teams[away].name} (away)\n"

    output += f"\nTotal number of breaks: {schedule.total_breaks_value}\n"
    return output