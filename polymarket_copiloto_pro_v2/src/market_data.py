import os
import requests

GAMMA = os.getenv("POLYMARKET_GAMMA", "https://gamma-api.polymarket.com")

def fetch_active_markets(limit: int = 250):
    """
    Fetch active Polymarket markets from the public Gamma API.
    This is read-only and does not require authentication.
    """
    params = {
        "active": "true",
        "closed": "false",
        "limit": limit,
        "order": "volume24hr",
        "ascending": "false",
    }
    r = requests.get(f"{GAMMA}/markets", params=params, timeout=30)
    r.raise_for_status()
    return r.json()
