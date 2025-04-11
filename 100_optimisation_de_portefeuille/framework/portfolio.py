class Portfolio:
    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.positions = {}

    def add_asset(self, asset, target_allocation):
        """
        Adds an asset to the portfolio with a target allocation (fraction, e.g., 0.25 for 25%).
        If the asset exists, its allocation is updated.
        Ensures the total allocation does not exceed 100%.
        """
        if target_allocation < 0 or target_allocation > 1:
            raise ValueError("Allocation must be between 0 and 1")

        # Calculate the new total allocation if we add this asset
        current_total_allocation = sum(pos['allocation'] for pos in self.positions.values())
        new_total_allocation = current_total_allocation + target_allocation

        if new_total_allocation > 1:
            raise ValueError(f"Total allocation exceeds 100%! Current: {current_total_allocation:.2f}, New: {new_total_allocation:.2f}")

        self.positions[asset] = {'allocation': target_allocation, 'shares': 0}

    def buy_asset(self, asset, amount):
        """
        Buys a given dollar amount of an asset.
        The number of shares purchased is calculated from the asset's current price.
        Cash is reduced accordingly.
        """
        if amount > self.cash:
            raise ValueError("Not enough cash to buy this asset")
        shares = amount / asset.price  # can be fractional shares, or use int() for whole shares
        self.positions[asset]['shares'] += shares
        self.cash -= amount

    def sell_asset(self, asset, amount):
        """
        Sells an asset for a given dollar amount.
        The number of shares to sell is calculated from the asset's current price.
        Cash is increased accordingly.
        """
        if asset not in self.positions:
            raise ValueError("Asset not in portfolio")
        shares_to_sell = amount / asset.price
        if shares_to_sell > self.positions[asset]['shares']:
            raise ValueError("Not enough shares to sell the requested amount")
        self.positions[asset]['shares'] -= shares_to_sell
        self.cash += amount

    def total_portfolio_value(self):
        """
        Returns the total portfolio value: cash + sum(value of each asset holding).
        """
        total_value = self.cash
        for asset, pos in self.positions.items():
            total_value += pos['shares'] * asset.price
        return total_value

    def current_allocations(self):
        """
        Returns a dictionary with current allocation percentages for each asset.
        """
        total_value = self.total_portfolio_value()
        allocations = {}
        for asset, pos in self.positions.items():
            asset_value = pos['shares'] * asset.price
            allocations[asset.name] = asset_value / total_value if total_value > 0 else 0
        return allocations

    def expected_portfolio_yield(self):
        """
        Calculates the expected total yield for the portfolio.
        This includes both the capital yield (yield_rate) and dividends from each asset.
        It is weighted by the asset's current value in the portfolio.
        """
        total_value = self.total_portfolio_value()
        portfolio_yield = 0.0
        for asset, pos in self.positions.items():
            asset_value = pos['shares'] * asset.price
            asset_total_yield = asset.yield_rate + asset.dividend_yield
            portfolio_yield += (asset_value / total_value) * asset_total_yield
        return portfolio_yield

    def rebalance(self):
        """
        Rebalances the portfolio so that each asset's value matches its target allocation.
        This method sells or buys assets as needed, assuming that transaction costs are ignored.
        The portfolio is rebalanced using the current total portfolio value.
        """
        total_value = self.total_portfolio_value()
        target_values = {asset: pos['allocation'] * total_value for asset, pos in self.positions.items()}

        for asset, pos in self.positions.items():
            current_value = pos['shares'] * asset.price
            difference = target_values[asset] - current_value
            if difference > 0:
                if difference > self.cash:
                    raise ValueError("Not enough cash to fully rebalance the portfolio")
                self.buy_asset(asset, difference)
            elif difference < 0:
                self.sell_asset(asset, -difference)

    def __str__(self):
        """
        String representation of the portfolio.
        """
        allocations = self.current_allocations()
        pos_str = ", ".join(f"{asset.name}: {alloc*100:.2f}%" for asset, alloc in zip(self.positions.keys(), allocations.values()))
        return f"Portfolio(Value: {self.total_portfolio_value():.2f}, Cash: {self.cash:.2f}, Allocations: {{{pos_str}}})"

