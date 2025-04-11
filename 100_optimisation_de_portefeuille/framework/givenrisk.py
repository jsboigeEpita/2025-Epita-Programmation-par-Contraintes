import cvxpy as cp
import numpy as np
import yfinance as yf
import pandas as pd


def get_stock_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    return data

# Function to compute expected returns and covariance matrix
def compute_metrics(price_data):
    returns = price_data.pct_change().dropna()
    mean_returns = returns.mean()  # Expected returns
    cov_matrix = returns.cov()  # Covariance matrix
    return mean_returns, cov_matrix

def optimize_portfolio(price_data, target_risk, max_alloc):
    mean_returns, cov_matrix = compute_metrics(price_data)
    num_assets = len(mean_returns)
    weights = cp.Variable(num_assets)  # Portfolio weights
    expected_return = mean_returns.values @ weights
    portfolio_risk = cp.quad_form(weights, cov_matrix.values)

    # Define optimization problem: maximize returns given target risk constraint
    objective = cp.Maximize(expected_return)
    constraints = [
        cp.sum(weights) == 1,         # Weights sum to 1
        weights >= 0,                  # No short selling
        portfolio_risk <= target_risk,   # Risk constraint
        cp.max(weights) <= max_alloc
    ]

    prob = cp.Problem(objective, constraints)
    prob.solve()

    return weights.value  # Optimized portfolio weights

# Main function to run the optimization
def solve(tickers, target_risk, start_date='2020-01-01', end_date='2024-01-01', max_alloc=1):
    # Fetch stock data
    price_data = get_stock_data(tickers, start_date, end_date)
    # Compute expected returns and covariance matrix

    # Optimize portfolio
    optimal_weights = optimize_portfolio(price_data, target_risk, max_alloc)

    # Display results
    return optimal_weights
