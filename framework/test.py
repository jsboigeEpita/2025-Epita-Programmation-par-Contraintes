from asset import Asset, get_asset_from_ticker

for i in ["RGC", "RCAT", "DOGZ", "DGNX", "ATGL", "CMRX"]:
    asset = get_asset_from_ticker(i)
    print(i, asset.yield_rate ,asset.sharpe_ratio(0))
