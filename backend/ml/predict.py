def estimate_trend(prices):
    if len(prices) < 2:
        return {"trend": "insufficient data", "estimated_next_price": None}
    prices = [float(p) for p in prices]
    change = prices[-1] - prices[0]
    avg_change = change / (len(prices) - 1)
    estimate = round(prices[-1] + avg_change, 2)
    trend = "increasing" if avg_change > 1 else "decreasing" if avg_change < -1 else "stable"
    return {"trend": trend, "estimated_next_price": estimate}
