# Placeholder for price service
# This file will contain functions to get mock or real cryptocurrency prices.

def get_current_mock_prices():
    """
    Returns a dictionary of current mock cryptocurrency prices.
    These values are intentionally slightly different from the chart's initial mock data.
    """
    return {
        'btc_usd': 35250.0,  # Example: Slightly different from initial chart mock
        'sol_usd': 121.5     # Example: Slightly different
    }

if __name__ == '__main__':
    # Example usage:
    prices = get_current_mock_prices()
    print(f"Current mock prices: BTC/USD = {prices['btc_usd']}, SOL/USD = {prices['sol_usd']}")
