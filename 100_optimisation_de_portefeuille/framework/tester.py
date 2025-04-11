from portfolio import Portfolio
from constraint import Constraint

class Backtester:
    def __init__(self, initial_cash, assets, constraint):
        """
        Initializes the backtester with assets, a portfolio, and optional constraints.
        :param initial_cash: Starting capital
        :param assets: List of Asset objects
        :param constraints: Constraint class
        """
        self.portfolio = Portfolio(initial_cash)
        self.assets = {asset.name: asset for asset in assets}
        self.constraint = constraint

    def apply_constraints(self):
        """
        Checks if the proposed allocations meet the constraints.
        :param allocations: Dict {asset_name: target_allocation}
        """
        self.constraint.check_constraints(self.portfolio)

    def test_allocation(self, allocations):
        """
        Tests an allocation strategy by applying constraints and computing expected yield.
        :param allocations: Dict {asset_name: target_allocation}
        :return: Portfolio expected yield if constraints are met, else None
        """
        asset_allocs = {self.assets[name]: alloc for name, alloc in allocations.items()}

        if not self.apply_constraints():
            print("❌ Allocation rejected due to constraints.")
            return None

        # Reset and rebalance portfolio
        self.portfolio = Portfolio(self.portfolio.cash)
        for asset, alloc in asset_allocs.items():
            self.portfolio.add_asset(asset, alloc)
        self.portfolio.rebalance()

        # Compute expected portfolio yield
        expected_yield = self.portfolio.expected_portfolio_yield()
        print(f"✅ Allocation accepted. Expected yield: {expected_yield:.2%}")
        return expected_yield

