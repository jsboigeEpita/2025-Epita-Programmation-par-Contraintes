from operator import ge
from flask import Flask, jsonify, request
# from asset import Asset, get_asset_from_ticker, get_stock_price_from_tickers
from asset import get_stock_price_from_tickers
from flask_cors import CORS
import givenrisk as gr
import sharpe_opti as so
import json

from AcoOptimizer import ACO
from PsoOptimizer import PSO
from AnnealingOptimizer import SimulatedAnnealingOptimizer
from PtfEvaluator import PortfolioEvaluator
from alternate_asset import *

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def greet():
    tickers = request.args.get('tickers')
    if(tickers == None):
        return jsonify(message="Bad request: missing tickers", status=400)
    data = tickers.split(",")
    assets = [get_asset_from_ticker(i) for i in data]
    optimal_weights = so.solve(assets)

    print(optimal_weights)
    stocks = get_stock_price_from_tickers(data)
    return [
        {
            "name": data[i],
            "percentage": optimal_weights[i],
            "data": stocks[i],
            "returns": assets[i].expected_return,
        }
        for i in range(len(data))
    ]

@app.route('/quad', methods=['GET'])
def quad_endpoint():
    tickers = request.args.get('tickers')
    volatility = request.args.get('volatility')

    if(tickers == None):
        return jsonify(message="Bad request: missing tickers", status=400)

    if(volatility == None):
        return jsonify(message="Bad request: invalid volatility", status=400)

    data = tickers.split(",")

    print("Quad endpoint called with tickers:", data)
    print("Volatility:", volatility)

    start_date = '2025-01-01'
    end_date = '2025-04-03'
    optimal_weights = gr.solve(tickers=data, target_risk=float(volatility), start_date=start_date, end_date=end_date)
    assets = [get_asset_from_ticker(i) for i in data]

    print(optimal_weights)
    stocks = get_stock_price_from_tickers(data)
    return [
        {
            "name": data[i],
            "percentage": optimal_weights[i],
            "data": stocks[i],
            "returns": assets[i].expected_return,
        }
        for i in range(len(data))
    ]

@app.route('/gen', methods=['GET'])
def gen_endpoint():
    tickers = request.args.get('tickers')
    method = request.args.get('method')
    constraints = json.loads(request.args.get('constraints'))

    print("Gen endpoint called with tickers:", tickers)
    print("Method:", method)
    print("Constraints:", constraints)

    if(tickers == None):
        return jsonify(message="Bad request: missing tickers", status=400)
    data = tickers.split(",")

    given_assets = [get_asset_from_ticker(i) for i in data]

    [print(str(a)) for a in given_assets]

    sector_limits = constraints.get('sector_limits', None)
    budget = constraints.get('budget', None)
    max_assets = constraints.get('max_assets', None)
    max_volatility = constraints.get('max_volatility', None)
    min_yield = constraints.get('min_yield', None)
    max_alloc_asset = constraints.get('max_alloc_asset', None)
    min_sharpe_ratio = constraints.get('min_sharpe_ratio', None)
    evaluator = PortfolioEvaluator(sector_limits=sector_limits, budget=budget, max_assets=max_assets, max_alloc=max_alloc_asset, max_vol=max_volatility, min_yield=min_yield, min_sharpe=min_sharpe_ratio)

    optimizer = None
    if method == "ACO":
        optimizer = ACO(given_assets, evaluator)
    elif method == "PSO":
        optimizer = PSO(given_assets, evaluator)
    elif method == "SA":
        optimizer = SimulatedAnnealingOptimizer(given_assets, evaluator)

    if optimizer is None:
        return jsonify(message="Bad request: invalid method", status=400)

    result = optimizer.optimize()

    stocks = None
    if result is None:
        stocks = get_stock_price_from_tickers(data)
    else:
        stocks = get_stock_price_from_tickers([a.name for a in result.assets])

    return jsonify([
    {
        "name": (result.assets[i].name) if result is not None else data[i],
        "percentage": result.weights[i] if result is not None else 0,
        "data": stocks[i],
        "returns": result.assets[i].expected_return if result is not None else 0,
    }
    for i in range((len(result.assets)) if result is not None else len(data))
])

if __name__ == '__main__':
    app.run(debug=True)
