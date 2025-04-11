import random
import numpy as np
import copy

from alternate_ptf import Portfolio

class ACO:
    def __init__(
        self,
        assets,
        evaluator,
        num_ants=20,
        max_iterations=100,
        alpha=1.0,    # pheromone importance
        beta=2.0,     # heuristic importance
        evaporation=0.1,
        q=1.0         # pheromone deposit factor
    ):
        self.assets = assets
        self.evaluator = evaluator
        self.asset_count = len(assets)
        self.num_ants = num_ants
        self.max_iterations = max_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.q = q

        # Initialize pheromone levels (1 per asset)
        self.pheromone = np.ones(self.asset_count)

    def _build_portfolio(self):
        """Construct a single ant's portfolio using pheromone + heuristic info."""
        selected = []
        available = list(range(self.asset_count))
        while len(selected) < self.evaluator.max_assets:
            probs = []
            for i in available:
                heuristic = max(self.assets[i].expected_return, 0)
                p = (self.pheromone[i] ** self.alpha) * (heuristic ** self.beta)
                probs.append(p)
            probs = np.array(probs)
            if np.sum(probs) == 0:
                probs = [1.0 / len(probs)] * len(probs)
            else:
                probs /= np.sum(probs)
            choice = np.random.choice(available, p=probs)
            selected.append(choice)
            available.remove(choice)

        # Assign weights (random dirichlet then normalize, clip max alloc)
        weights = [0.0] * self.asset_count
        raw_weights = np.random.dirichlet(np.ones(len(selected)))
        for idx, w in zip(selected, raw_weights):
            weights[idx] = min(w, self.evaluator.max_alloc)

        total = sum(weights)
        if total > 0:
            weights = [w / total for w in weights]

        portfolio = Portfolio(self.assets, weights)
        return portfolio if self.evaluator.is_feasible(portfolio) else None

    def _update_pheromones(self, solutions):
        # Evaporate
        self.pheromone *= (1 - self.evaporation)

        # Add pheromone based on solution quality
        for portfolio in solutions:
            score = portfolio.total_return()
            for i, weight in enumerate(portfolio.weights):
                if weight > 0:
                    self.pheromone[i] += self.q * score * weight

    def optimize(self):
        print("[ACO OPTIMIZER]")
        best_portfolio = None
        best_score = -np.inf

        print("Starting optimization with ant portfolio creation...")
        for _ in range(self.max_iterations):
            solutions = []
            for _ in range(self.num_ants):
                portfolio = self._build_portfolio()
                if portfolio:
                    solutions.append(portfolio)
                    score = portfolio.total_return()
                    if score > best_score:
                        best_score = score
                        best_portfolio = portfolio

            if solutions:
                print("Updating pheromones...")
                self._update_pheromones(solutions)

        print("Best Portfolio Found!")
        return best_portfolio

