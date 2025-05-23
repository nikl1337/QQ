import pytest
from app.services.price_service import get_current_mock_prices

def test_get_current_mock_prices():
    """
    Tests the get_current_mock_prices function.
    """
    prices = get_current_mock_prices()

    # Check if it returns a dictionary
    assert isinstance(prices, dict), "Should return a dictionary"

    # Check for expected keys
    assert "btc_usd" in prices, "Should contain 'btc_usd' key"
    assert "sol_usd" in prices, "Should contain 'sol_usd' key"

    # Check if values are numeric (int or float)
    assert isinstance(prices["btc_usd"], (int, float)), "'btc_usd' should be a number"
    assert isinstance(prices["sol_usd"], (int, float)), "'sol_usd' should be a number"

    # Optional: Check for positive values if that's an invariant
    assert prices["btc_usd"] > 0, "'btc_usd' should be positive"
    assert prices["sol_usd"] > 0, "'sol_usd' should be positive"

# To run this test:
# 1. Ensure pytest is installed.
# 2. Navigate to the `backend` directory (or project root).
# 3. Run `pytest` or `python -m pytest`.
# Ensure paths are correctly set up for imports.
# This test assumes `backend.` prefix for imports when run from project root.
