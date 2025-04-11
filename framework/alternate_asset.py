from stockdex import Ticker

class Asset:
    def __init__(self, name, price, expected_return, volatility, quantity, sector, sharpe_ratio=0.0):
        self.name = name
        self.price = price
        self.expected_return = expected_return
        self.volatility = volatility
        self.quantity = quantity
        self.sector = sector
        self._sharpe = sharpe_ratio

    def sharpe_ratio(self):
        return self._sharpe

    def total_expected_return(self):
        return self.expected_return

    def __str__(self):
        return f"Ticker: {self.name}\nPrice: {self.price}\nExpected Return: {self.expected_return}\nVolatility: {self.volatility}\nSector: {self.sector}"

def get_average_yield_rate(ticker_symbol):
    stock = Ticker(ticker=ticker_symbol)
    price_data = stock.yahoo_api_price(range='5d', dataGranularity='1d')
    price_data.sort_index(inplace=True)
    price_data['daily_return'] = price_data['close'].pct_change()
    average_daily_return = price_data['daily_return'].mean()
    average_annual_return = average_daily_return * 5  # Five days
    return average_annual_return

def get_asset_from_ticker(ticker):
    stock = Ticker(ticker=ticker)
    data = stock.yahoo_api_price(range='1d', dataGranularity='1d').transpose()[0]
    data_sum = stock.yahoo_web_summary.transpose()
    name = ticker
    price = data["close"]
    volatility = data_sum.get('fiftyTwoWeekRange', 0.0)[0].split("-")
    volatility = (float(volatility[1].replace(",","")) - float(volatility[0].replace(",","")))
    volatility = volatility / price
    return Asset(name, price, get_average_yield_rate(ticker), volatility, 0, None)
