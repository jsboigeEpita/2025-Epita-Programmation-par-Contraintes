class Portfolio:
    def __init__(self, assets, weights):
        self.assets = assets
        self.weights = weights

    def total_return(self):
        return sum(asset.total_expected_return() * weight for asset, weight in zip(self.assets, self.weights))

    def total_volatility(self):
        return sum(asset.volatility * weight for asset, weight in zip(self.assets, self.weights))

    def sharpe_ratio(self, risk_free_rate=0.02):
        return (self.total_return() - risk_free_rate) / self.total_volatility()
