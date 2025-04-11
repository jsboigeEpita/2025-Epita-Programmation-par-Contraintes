from ortools.linear_solver import pywraplp

def solve(assets, max_assets=10, max_asset_allocation=0.4 ,max_sector_allocation=0.4, 
                       min_sharpe_ratio=0, max_volatility= 10000, target_return=0.07):
    
    solver = pywraplp.Solver.CreateSolver("SCIP")
    n = len(assets)

    x = [solver.NumVar(0.0, 1.0, f'x_{i}') for i in range(n)]  # allocation (0-100%)
    y = [solver.IntVar(0, 1, f'y_{i}') for i in range(n)]       # actif sélectionné ou non

    # Contraintes : si y[i] == 0 alors x[i] == 0
    for i in range(n):
        solver.Add(x[i] <= y[i])

    # Contraintes : nombre maximum d'actifs
    solver.Add(solver.Sum(y[i] for i in range(n)) <= max_assets)

    # Contraintes : Sharpe minimum et volatilité
    for i, asset in enumerate(assets):
        if asset.sharpe_ratio() < min_sharpe_ratio or asset.volatility > max_volatility:
            # Empêche d'investir dans ces actifs
            solver.Add(x[i] == 0)
            solver.Add(y[i] == 0)

    # Contraintes : allocation totale == 1 (100%)
    solver.Add(solver.Sum(x[i] for i in range(n)) == 1.0)

    #Contraintes: allocation par asset
    for i in range(n):
        solver.Add(x[i] <= max_asset_allocation)
    # Contraintes sectorielles
    #sectors = {}
    #for i, asset in enumerate(assets):
    #    if asset.sector:
    #        sectors.setdefault(asset.sector, []).append(i)

    #for sector, indices in sectors.items():
    #    solver.Add(solver.Sum(x[i] for i in indices) <= max_sector_allocation)

    # Contraintes : rendement attendu
    expected_returns = [asset.total_expected_return() for asset in assets]
    solver.Add(solver.Sum(x[i] * expected_returns[i] for i in range(n)) >= target_return)

    # Objectif : maximiser le rendement attendu du portefeuille
    objective = solver.Sum(x[i] * expected_returns[i] for i in range(n))
    solver.Maximize(objective)

    status = solver.Solve()

    return [x[i].solution_value() for i in range(n)]
    if status == pywraplp.Solver.OPTIMAL:
        print("Portefeuille optimal trouvé:")
        for i, asset in enumerate(assets):
            if x[i].solution_value() > 0.001:
                print(f"- {asset.name}: {x[i].solution_value() * 100:.2f}%")
    else:
        print("Pas de solution optimale trouvée.")


