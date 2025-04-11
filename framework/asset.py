from stockdex import Ticker
import json

class Asset:
    def __init__(self, name, price, yield_rate, volatility, currency='USD', sector=None, dividend_yield=0.0):
        self.name = name
        self.price = price
        self.yield_rate = yield_rate
        self.volatility = volatility
        self.currency = currency
        self.sector = sector
        self.dividend_yield = dividend_yield

    def total_expected_return(self):
        return self.yield_rate + self.dividend_yield

    def sharpe_ratio(self, risk_free_rate=0.02):
        """
        Calcule le Sharpe Ratio en supposant que le yield_rate est annualisé
        (Ratio entre la rentabilité excédentaire et la volatilité)
        """
        return (self.total_expected_return() - risk_free_rate) / self.volatility

    def __str__(self):
        return f"Ticker: {self.name}\nPrice: {self.price}{self.currency}\nYield_rate: {self.yield_rate}\nVolatility: {self.volatility}\nSector: {self.sector}\nDividend: {self.dividend_yield}"
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)

def get_average_yield_rate(ticker_symbol):
    stock = Ticker(ticker=ticker_symbol)
    price_data = stock.yahoo_api_price(range='5d', dataGranularity='1d')
    price_data.sort_index(inplace=True)
    price_data['daily_return'] = price_data['close'].pct_change()
    average_daily_return = price_data['daily_return'].mean()
    average_annual_return = average_daily_return * 5  # Five days
    return average_annual_return

def get_stock_price_from_tickers(tickers):
    res = []
    for tick in tickers:
        stock = Ticker(tick)
        data = stock.yahoo_api_price(range='5d', dataGranularity='1d')
        res.append(((data['open'] + data['close']) / 2).tolist())
    return res

def get_asset_from_ticker(ticker):
    stock = Ticker(ticker=ticker)
    data = stock.yahoo_api_price(range='1d', dataGranularity='1d').transpose()[0]
    data_sum = stock.yahoo_web_summary.transpose()
    name = ticker
    #price = data_sum.get('regularMarketDayRange', 0.0)[0].split("-")
    price = data["close"]
    currency = data.get('currency', 'USD')
    volatility = data_sum.get('fiftyTwoWeekRange', 0.0)[0].split("-")
    volatility = (float(volatility[1].replace(",","")) - float(volatility[0].replace(",","")))
    return Asset(name, price, get_average_yield_rate(ticker), volatility, currency)
