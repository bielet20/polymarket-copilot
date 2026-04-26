import os
import time
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

HOST = os.getenv("POLYMARKET_HOST", "https://clob.polymarket.com")
CHAIN_ID = int(os.getenv("POLYMARKET_CHAIN_ID", "1"))
PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY", "")
API_KEY = os.getenv("POLYMARKET_API_KEY", "")
API_SECRET = os.getenv("POLYMARKET_API_SECRET", "")
API_PASSPHRASE = os.getenv("POLYMARKET_API_PASSPHRASE", "")
FUNDER_ADDRESS = os.getenv("POLYMARKET_FUNDER_ADDRESS", "")

_client = None


def get_client():
    global _client
    if _client is not None:
        return _client

    if not PRIVATE_KEY:
        raise RuntimeError(
            "POLYMARKET_PRIVATE_KEY no configurada. "
            "Edita .env y añade tu clave privada."
        )

    try:
        from py_clob_client.client import ClobClient
        from py_clob_client.clob_types import ApiCreds
    except ImportError:
        raise RuntimeError(
            "Instala py-clob-client: pip install py-clob-client"
        )

    creds = ApiCreds(
        api_key=API_KEY,
        api_secret=API_SECRET,
        api_passphrase=API_PASSPHRASE,
    ) if API_KEY else None

    _client = ClobClient(
        host=HOST,
        chain=CHAIN_ID,
        key=PRIVATE_KEY,
        creds=creds,
        funder=FUNDER_ADDRESS,
    )
    return _client


def get_token_id(market_slug: str) -> Optional[str]:
    client = get_client()
    try:
        markets = client.get_markets(market_slug=market_slug)
        if markets and len(markets) > 0:
            return markets[0].get("token_id")
    except Exception:
        pass
    return None


def place_buy_order(
    token_id: str,
    price: float,
    size: float,
    confirm: bool = False
) -> dict:
    if not confirm:
        return {
            "status": "preview",
            "token_id": token_id,
            "price": price,
            "size": size,
            "cost": price * size,
            "message": "Usa confirm=True para ejecutar"
        }

    client = get_client()
    from py_clob_client.order_builder.constants import BUY

    order = client.create_and_post_order(
        OrderArgs(token_id=token_id, price=price, size=size, side=BUY),
        options={"tick_size": "0.01", "neg_risk": False}
    )
    return {"status": "submitted", "order": order}


def get_balance() -> float:
    client = get_client()
    try:
        balance = client.get_balance()
        return float(balance)
    except Exception:
        return 0.0


def get_orders() -> list:
    client = get_client()
    try:
        return client.get_orders()
    except Exception:
        return []
