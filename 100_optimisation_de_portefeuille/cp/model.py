from ortools.sat.python import cp_model
from framework.asset import Asset

assets = [
            Asset("APPL", 54, 0.14, 30, "TECH", 0.1 ),
            Asset("GOOGL", 312, 0.11, 10, "TECH"),
            Asset("AMZN", 98, 0.09, 20, "COMMERCE", 0.12 ),
            Asset("MSFT", 948, 0.27, 50, "TECH", 0.15 ),
            Asset("TSLA", 12, 0.2, 70, "AUTO", 0.13 ),
         ]
N = len(assets)
sector_limits = {"Tech": 0.6, "E-commerce": 0.3, "Auto": 0.2}  # % max par secteur

# Contraintes
budget = 1.0  # 100% du capital
max_assets = 3  # Nombre max d'actifs
max_volatility = 0.3  # Volatilité max par actif
min_yield = 0.09  # Rendement minimal par actif
max_alloc_asset = 0.4  # % max par actif
min_sharpe_ratio = 1.2  # Ratio de Sharpe min par actif

model = cp_model.CpModel()

# Variables
x = [model.NewBoolVar(f"x_{i}") for i in range(N)]  # Actif sélectionné (1/0)
w = [model.NewIntVar(0, int(budget * 100), f"w_{i}") for i in range(N)]  # Allocation * 100 pour éviter les flottants

# Contraintes
model.Add(sum(x) <= max_assets)  # Nombre max d'actifs sélectionnés

for i in range(N):
    model.Add(w[i] <= (max_alloc_asset * budget) * 100)  # Allocation max par actif
    model.Add(w[i] >= min_yield * budget * x[i] * 100)  # Rendement min conditionnel
    model.Add(assets[i].volatility * x[i] <= max_volatility)  # Volatilité max conditionnelle
    model.Add(assets[i].sharpe_ratio() * x[i] >= min_sharpe_ratio)  # Sharpe ratio min

# Allocation totale = budget
model.Add(sum(w) == budget * 100)

# Contraintes sectorielles
for sector in set([s.sector for s in assets]):
    sector_indices = [i for i in range(N) if assets[i].sector == sector]
    model.Add(sum(w[i] for i in sector_indices) <= sector_limits[sector] * budget * 100)

# Fonction objectif : maximiser le rendement
model.Maximize(sum(w[i] * assets[i].total_expected_return() for i in range(N)))

# Résolution
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Résultats
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for i in range(N):
        if solver.Value(x[i]) == 1:
            print(f"Investir {solver.Value(w[i]) / 100:.2f} dans {assets[i]}")
else:
    print("Aucune solution trouvée.")

