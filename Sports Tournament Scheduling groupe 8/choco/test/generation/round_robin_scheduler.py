from itertools import combinations

def generate_schedule(teams, stadiums=None, unavailable_dates=None, constraints=None):
    if len(teams) % 2 != 0:
        teams.append("BYE")

    n = len(teams)
    rounds = []
    for i in range(n - 1):
        round_matches = []
        for j in range(n // 2):
            t1 = teams[j]
            t2 = teams[n - 1 - j]
            if i % 2 == 0:
                round_matches.append({"home": t1, "away": t2})
            else:
                round_matches.append({"home": t2, "away": t1})
        teams.insert(1, teams.pop())
        rounds.append(round_matches)

    return rounds
