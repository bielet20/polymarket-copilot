import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("POLYMARKET_HOST", "https://clob.polymarket.com")
CHAIN_ID = int(os.getenv("POLYMARKET_CHAIN_ID", "137"))
PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY", "")
FUNDER_ADDRESS = os.getenv("POLYMARKET_FUNDER_ADDRESS", "")

_client = None
_creds = None


def get_client():
    global _client, _creds

    print(f"DEBUG: PRIVATE_KEY length = {len(PRIVATE_KEY)}")
    print(f"DEBUG: PRIVATE_KEY starts with = {PRIVATE_KEY[:10] if PRIVATE_KEY else 'EMPTY'}")

    if PRIVATE_KEY and not _client:
        try:
            from py_clob_client_v2 import ApiCreds, ClobClient, OrderArgs
            from py_clob_client_v2.order_builder.constants import BUY
        except ImportError:
            raise RuntimeError("Instala py-clob-client: pip install py-clob-client-v2")

        _client = ClobClient(
            host=HOST,
            chain_id=CHAIN_ID,
            key=PRIVATE_KEY,
            funder=FUNDER_ADDRESS,
        )

        API_KEY = os.getenv("POLYMARKET_API_KEY", "")
        API_SECRET = os.getenv("POLYMARKET_API_SECRET", "")
        API_PASSPHRASE = os.getenv("POLYMARKET_API_PASSPHRASE", "")

        if API_KEY and API_SECRET and API_PASSPHRASE:
            _creds = ApiCreds(
                api_key=API_KEY,
                api_secret=API_SECRET,
                api_passphrase=API_PASSPHRASE,
            )
        else:
            print("Generando API credentials automáticamente...")
            _creds = _client.create_or_derive_api_key()
            print(f"apiKey: {_creds['apiKey']}")
            print(f"secret: {_creds['secret']}")
            print(f"passphrase: {_creds['passphrase']}")
            print("\nAñade estas credenciales a tu .env para no generarlas cada vez")

    if _client is None:
        raise RuntimeError(
            "POLYMARKET_PRIVATE_KEY no configurada. "
            "Edita .env y añade tu clave privada."
        )

    return _client


def get_token_id(market_slug: str):
    client = get_client()
    try:
        markets = client.get_markets(market_slug=market_slug)
        if markets and len(markets) > 0:
            return markets[0].get("token_id")
    except Exception:
        pass
    return None


def place_buy_order(token_id: str, price: float, size: float, confirm: bool = False):
    from py_clob_client_v2 import OrderArgs
    from py_clob_client_v2.order_builder.constants import BUY

    if not confirm:
        return {
            "status": "preview",
            "token_id": token_id,
            "price": price,
            "size": size,
            "cost": price * size,
            "message": "Usa --confirm para ejecutar"
        }

    client = get_client()

    order = client.create_and_post_order(
        order_args=OrderArgs(
            token_id=token_id,
            price=price,
            size=size,
            side=BUY,
        ),
        options={"tick_size": "0.01", "neg_risk": False}
    )
    return {"status": "submitted", "order": order}


def get_balance():
    client = get_client()
    try:
        balance = client.get_balance()
        return float(balance)
    except Exception:
        return 0.0


def get_orders():
    client = get_client()
    try:
        return client.get_orders()
    except Exception:
        return []