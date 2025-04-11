import random
import copy
import numpy as np

from alternate_ptf import Portfolio

class PSO:
    def __init__(
        self,
        assets,
        evaluator,
        num_particles=30,
        max_iterations=100,
        w=0.5,           # inertia
        c1=1.5,          # cognitive
        c2=1.5           # social
    ):
        self.assets = assets
        self.evaluator = evaluator
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.asset_count = len(assets)

    def _random_feasible_portfolio(self):
        """Generate a portfolio with at most max_assets non-zero weights."""
        max_assets = self.evaluator.max_assets
        while True:
            indices = random.sample(range(self.asset_count), max_assets)
            weights = [0.0] * self.asset_count
            raw_weights = np.random.dirichlet(np.ones(len(indices)))

            for idx, w in zip(indices, raw_weights):
                weights[idx] = min(w, self.evaluator.max_alloc)

            total = sum(weights)
            if total > 0:
                weights = [w / total for w in weights]

            candidate = Portfolio(self.assets, weights)
            if self.evaluator.is_feasible(candidate):
                return weights

    def optimize(self):
        print("[PSO OPTIMIZER]")

        # Initialize particles
        particles = []
        print("Initializing particles...")
        while len(particles) < self.num_particles:
            w = self._random_feasible_portfolio()
            if w:
                particles.append(w)

        velocities = [np.zeros(self.asset_count) for _ in range(self.num_particles)]

        personal_best = copy.deepcopy(particles)
        personal_best_scores = [
            Portfolio(self.assets, p).total_return() for p in personal_best
        ]

        global_best = personal_best[np.argmax(personal_best_scores)]
        global_best_score = max(personal_best_scores)

        print("Starting optimization by moving particules...")
        for _ in range(self.max_iterations):
            for i in range(self.num_particles):
                r1 = np.random.rand(self.asset_count)
                r2 = np.random.rand(self.asset_count)

                # Velocity update
                velocities[i] = (
                    self.w * velocities[i]
                    + self.c1 * r1 * (np.array(personal_best[i]) - np.array(particles[i]))
                    + self.c2 * r2 * (np.array(global_best) - np.array(particles[i]))
                )

                # Position update
                new_position = np.array(particles[i]) + velocities[i]

                # Enforce max_assets: keep only top-k weights
                top_indices = np.argsort(-new_position)[:self.evaluator.max_assets]
                new_weights = [0.0] * self.asset_count
                for idx in top_indices:
                    new_weights[idx] = max(0, new_position[idx])  # no negatives

                total = sum(new_weights)
                if total > 0:
                    new_weights = [w / total for w in new_weights]

                new_weights = [min(w, self.evaluator.max_alloc) for w in new_weights]
                total = sum(new_weights)
                if total > 0:
                    new_weights = [w / total for w in new_weights]

                portfolio = Portfolio(self.assets, new_weights)
                score = portfolio.total_return() if self.evaluator.is_feasible(portfolio) else -np.inf

                if score > personal_best_scores[i]:
                    personal_best[i] = new_weights
                    personal_best_scores[i] = score
                    if score > global_best_score:
                        global_best = new_weights
                        global_best_score = score

                particles[i] = new_weights

        print("Best portfolio found!")
        return Portfolio(self.assets, global_best)

