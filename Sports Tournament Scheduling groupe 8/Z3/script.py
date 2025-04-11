from z3 import *

def sports_tournament_schedule(n=6):
    # n doit être pair.
    rounds = n - 1
    games_per_round = n // 2

    # Création des variables :
    # Pour chaque round r et chaque match g, on définit home[r][g] et away[r][g]
    # représentant respectivement l'équipe jouant à domicile et l'équipe à l'extérieur.
    home = [[Int(f"home_{r}_{g}") for g in range(games_per_round)] for r in range(rounds)]
    away = [[Int(f"away_{r}_{g}") for g in range(games_per_round)] for r in range(rounds)]
    
    opt = Optimize()
    
    # Optionnel : activer le parallélisme interne de Z3 (si supporté)
    set_option("parallel.enable", True)

    # Contrainte de domaine : chaque variable est une équipe entre 0 et n-1,
    # et une équipe ne peut pas jouer contre elle-même.
    for r in range(rounds):
        for g in range(games_per_round):
            opt.add(home[r][g] >= 0, home[r][g] < n)
            opt.add(away[r][g] >= 0, away[r][g] < n)
            opt.add(home[r][g] != away[r][g])

    # Contrainte : chaque équipe doit apparaître une et une seule fois par journée.
    for r in range(rounds):
        teams_in_round = []
        for g in range(games_per_round):
            teams_in_round.append(home[r][g])
            teams_in_round.append(away[r][g])
        opt.add(Distinct(teams_in_round))
    
    # Contrainte : chaque paire d’équipes se rencontre exactement une fois dans le tournoi.
    for i in range(n):
        for j in range(i + 1, n):
            occurrences = []
            for r in range(rounds):
                for g in range(games_per_round):
                    occurrences.append(If(Or(And(home[r][g] == i, away[r][g] == j),
                                             And(home[r][g] == j, away[r][g] == i)), 1, 0))
            opt.add(Sum(occurrences) == 1)

    # Optimisation : Minimiser le nombre total de breaks.
    # Un break est défini pour une équipe lorsqu'elle reste dans le même statut (domicile ou extérieur)
    # dans deux rounds consécutifs.
    break_expr = []
    for i in range(n):
        for r in range(rounds - 1):
            is_home_r = Sum([If(home[r][g] == i, 1, 0) for g in range(games_per_round)])
            is_home_r_next = Sum([If(home[r+1][g] == i, 1, 0) for g in range(games_per_round)])
            break_expr.append(If(is_home_r == is_home_r_next, 1, 0))
    total_breaks = Sum(break_expr)
    opt.minimize(total_breaks)
    
    # Contrainte implicite sur la parité : le nombre total de breaks doit être pair.
    # opt.add(total_breaks % 2 == 0)
    # opt.add(total_breaks == n - 2) 
    
    # Symétrie : On fixe la première journée.
    # Par exemple, dans la première journée, on impose que le premier match oppose l'équipe 0 (domicile)
    # à une équipe d'indice > 0 (extérieur) et que les équipes jouant à domicile sont ordonnées.
    if games_per_round > 0:
        opt.add(home[0][0] == 0)
        # Pour éviter la symétrie d'inversion domicile/extérieur, on impose que l'équipe extérieure
        # du premier match a un indice supérieur à l'équipe à domicile.
        opt.add(away[0][0] > home[0][0])
    # On impose un ordre croissant pour les équipes jouant à domicile dans la première journée
    for g in range(1, games_per_round):
        opt.add(home[0][g-1] < home[0][g])
    
    # (Optionnel) On peut fixer le planning de la première équipe pour réduire les permutations
    # Exemple : forcer que l'équipe 0 joue ses adversaires dans un ordre croissant.
    # Pour chaque round, si l'équipe 0 apparaît, on impose que son adversaire soit supérieur à 0.
    for r in range(rounds):
        for g in range(games_per_round):
            opt.add(Implies(home[r][g] == 0, away[r][g] > 0))
            opt.add(Implies(away[r][g] == 0, home[r][g] > 0))
    
    # Recherche d'une solution optimale
    if opt.check() == sat:
        model = opt.model()
        print(f"Solution trouvée avec {model.evaluate(total_breaks)} breaks")
        for r in range(rounds):
            print(f"\nJournée {r+1}:")
            for g in range(games_per_round):
                home_team = model.evaluate(home[r][g])
                away_team = model.evaluate(away[r][g])
                print(f"  Match {g+1} : Équipe {home_team} (domicile) vs Équipe {away_team} (extérieur)")
    else:
        print("Aucune solution trouvée.")

if __name__ == "__main__":
    # Par exemple avec 6 équipes (n doit être pair)
    sports_tournament_schedule(n=4)
    