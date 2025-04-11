import random
import math
import copy
from alternate_ptf import Portfolio

class SimulatedAnnealingOptimizer:
    def __init__(self, assets, evaluator, initial_temp=1.0, cooling_rate=0.95, max_steps=1000):
        self.assets = assets
        self.evaluator = evaluator
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.max_steps = max_steps

    def random_portfolio(self):
        sorted_assets = sorted(self.assets, key=lambda a: a.total_expected_return() / (a.volatility + 1e-6), reverse=True)
        weights = [0.0] * len(self.assets)
        sector_usage = {}
        total_alloc = 0.0

        for asset in sorted_assets:
            i = self.assets.index(asset)
            sector = asset.sector.lower() if asset.sector else "other"
            sector_cap = self.evaluator.sector_limits.get(sector, 1.0)

            # Skip if adding this asset would break constraints
            if asset.volatility > self.evaluator.max_vol or asset.expected_return < self.evaluator.min_yield:
                continue
            if asset.sharpe_ratio() < self.evaluator.min_sharpe:
                continue
            if sector_usage.get(sector, 0) >= sector_cap:
                continue
            if total_alloc >= self.evaluator.budget:
                break

            alloc = min(self.evaluator.max_alloc, sector_cap - sector_usage.get(sector, 0), self.evaluator.budget - total_alloc)
            if alloc <= 0:
                continue

            weights[i] = alloc
            total_alloc += alloc
            sector_usage[sector] = sector_usage.get(sector, 0) + alloc

            if sum(1 for w in weights if w > 0) >= self.evaluator.max_assets:
                break

        # Normalize weights if needed
        if total_alloc > 0:
            weights = [w / total_alloc for w in weights]

        return Portfolio(self.assets, weights)

    def perturb(self, portfolio):
        new_weights = portfolio.weights[:]
        idx = random.randint(0, len(new_weights) - 1)
        change = random.uniform(-0.1, 0.1)
        new_weights[idx] = max(0.0, min(new_weights[idx] + change, self.evaluator.max_alloc))

        # Normalize
        total = sum(new_weights)
        if total > 0:
            new_weights = [w / total for w in new_weights]
        return Portfolio(self.assets, new_weights)

    def optimize(self):
        print("[ANNEALING OPTIMIZER]")

        print("Creating initial random Portfolio...")
        current = self.random_portfolio()
        while not self.evaluator.is_feasible(current):
            current = self.random_portfolio()

        best = copy.deepcopy(current)
        temperature = self.initial_temp

        print("Perturbing Portfolio...")
        for step in range(self.max_steps):
            neighbor = self.perturb(current)
            if not self.evaluator.is_feasible(neighbor):
                continue

            delta = neighbor.total_return() - current.total_return()
            if delta > 0 or random.random() < math.exp(delta / (temperature + 1e-6)):
                current = neighbor

            if current.total_return() > best.total_return():
                best = copy.deepcopy(current)

            temperature *= self.cooling_rate

        print("Best Portfolio found!")
        return best

