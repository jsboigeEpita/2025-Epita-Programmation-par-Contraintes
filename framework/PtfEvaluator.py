class PortfolioEvaluator:
    def __init__(self, budget=None, max_assets=None, max_vol=None, min_yield=None, max_alloc=None,
                 min_sharpe=None, sector_limits=None):
        self.budget = budget
        self.max_assets = max_assets
        self.max_vol = max_vol
        self.min_yield = min_yield
        self.max_alloc = max_alloc
        self.min_sharpe = min_sharpe
        self.sector_limits = sector_limits or {}

    def is_feasible(self, portfolio):
        selected_assets = [(a, w) for a, w in zip(portfolio.assets, portfolio.weights) if w > 0]
        if self.max_assets and len(selected_assets) > self.max_assets:
            return False

        total_alloc = sum(portfolio.weights)
        if self.budget and abs(total_alloc - self.budget) > 1e-3:
            return False

        for a, w in selected_assets:
            if self.max_alloc and w > self.max_alloc:
                return False
            if self.max_vol and a.volatility > self.max_vol:
                return False
            if self.min_yield and a.expected_return < self.min_yield:
                return False
            if self.min_sharpe and a.sharpe_ratio() < self.min_sharpe:
                return False

        if self.sector_limits:
            sector_totals = {}
            for a, w in selected_assets:
                sector = a.sector.lower()
                sector_totals[sector] = sector_totals.get(sector, 0) + w

            for s, max_pct in self.sector_limits.items():
                if sector_totals.get(s.lower(), 0) > max_pct:
                    return False

        return True

