from PtfEvaluator import PortfolioEvaluator
from alternate_asset import Asset

from AnnealingOptimizer import SimulatedAnnealingOptimizer
from PsoOptimizer import PSO
from AcoOptimizer import ACO

assets = [
    # Tech
    Asset("AAPL", 154, 0.14, 0.1, 30, "TECH", 1.2),
    Asset("GOOGL", 312, 0.11, 0.18, 10, "TECH", 1.15),
    Asset("MSFT", 298, 0.13, 0.12, 20, "TECH", 1.25),
    Asset("NVDA", 654, 0.18, 0.22, 15, "TECH", 1.3),
    Asset("META", 242, 0.12, 0.15, 10, "TECH", 1.1),

    # Commerce
    Asset("AMZN", 98, 0.09, 0.12, 20, "COMMERCE", 1.05),
    Asset("EBAY", 45, 0.08, 0.09, 50, "COMMERCE", 1.0),
    Asset("WMT", 147, 0.07, 0.08, 30, "COMMERCE", 1.1),
    Asset("COST", 508, 0.1, 0.1, 25, "COMMERCE", 1.2),
    Asset("BABA", 85, 0.11, 0.13, 40, "COMMERCE", 1.3),

    # Auto
    Asset("TSLA", 212, 0.2, 0.13, 70, "AUTO", 1.35),
    Asset("F", 12, 0.08, 0.07, 200, "AUTO", 1.0),
    Asset("GM", 34, 0.09, 0.08, 100, "AUTO", 1.05),
    Asset("RIVN", 15, 0.13, 0.2, 150, "AUTO", 1.1),
    Asset("NIO", 9, 0.12, 0.18, 200, "AUTO", 1.2),

    # Finance
    Asset("JPM", 143, 0.09, 0.11, 50, "FINANCE", 1.1),
    Asset("BAC", 33, 0.07, 0.1, 120, "FINANCE", 1.0),
    Asset("GS", 368, 0.1, 0.12, 20, "FINANCE", 1.15),
    Asset("MS", 90, 0.08, 0.09, 80, "FINANCE", 1.05),
    Asset("V", 227, 0.11, 0.1, 40, "FINANCE", 1.2),
]


sector_limits = {"TECH": 0.6, "COMMERCE": 0.3, "AUTO": 0.6}
budget = 1.0
max_assets = 5
max_volatility = 0.3
min_yield = 0.09
max_alloc_asset = 0.4
min_sharpe_ratio = 1.2

evaluator = PortfolioEvaluator(sector_limits=sector_limits, budget=budget, max_assets=max_assets, max_alloc=max_alloc_asset, max_vol=max_volatility, min_yield=min_yield, min_sharpe=min_sharpe_ratio)

optimizer1 = SimulatedAnnealingOptimizer(assets, evaluator)
optimizer2 = PSO(assets, evaluator)
optimizer3 = ACO(assets, evaluator)

best1= optimizer1.optimize()
best2= optimizer2.optimize()
best3= optimizer3.optimize()

print("Best portfolio with SA:")
for asset, weight in zip(best1.assets, best1.weights):
    if weight > 0:
        print(f"{asset.name}: {weight:.2f}")
print(f"Total return: {best1.total_return():.4f}")
print(f"Sharpe ratio: {best1.sharpe_ratio():.2f}")

print("Best portfolio with PSO:")
for asset, weight in zip(best2.assets, best2.weights):
    if weight > 0:
        print(f"{asset.name}: {weight:.2f}")
print(f"Total return: {best2.total_return():.4f}")
print(f"Sharpe ratio: {best2.sharpe_ratio():.2f}")

print("Best portfolio with ACO:")
for asset, weight in zip(best3.assets, best3.weights):
    if weight > 0:
        print(f"{asset.name}: {weight:.2f}")
print(f"Total return: {best3.total_return():.4f}")
print(f"Sharpe ratio: {best3.sharpe_ratio():.2f}")
