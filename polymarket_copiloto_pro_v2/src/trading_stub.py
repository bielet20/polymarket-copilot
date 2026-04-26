"""
Trading stub.

This file is intentionally not wired into main.py.

Reason:
- A professional system should prove signal quality first.
- Live trading should require explicit human confirmation.
- Your private keys should never be pasted into chat.

Future integration:
- Use Polymarket's official Python CLOB client.
- Load credentials from .env.
- Create signed limit orders only after manual confirmation.
"""

def place_order_disabled(*args, **kwargs):
    raise RuntimeError(
        "Live trading is disabled. Use scanner mode first and enable only after manual review."
    )
