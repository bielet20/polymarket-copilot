from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

SIGNALS_PATH = DATA_DIR / "signals.csv"
PRICE_HISTORY_PATH = DATA_DIR / "price_history.csv"


def save_signals(signals: list[dict]) -> Path:
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for signal in signals:
        row = dict(signal)
        row["created_at_utc"] = now
        rows.append(row)

    df = pd.DataFrame(rows)
    if SIGNALS_PATH.exists():
        old = pd.read_csv(SIGNALS_PATH)
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(SIGNALS_PATH, index=False)
    return SIGNALS_PATH


def load_signals() -> pd.DataFrame:
    if not SIGNALS_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(SIGNALS_PATH)


def _extract_snapshot_price(market: dict) -> float:
    from src.strategy import extract_price
    return extract_price(market)


def save_price_snapshot(markets: list[dict]) -> Path:
    now = datetime.now(timezone.utc).isoformat()
    rows = []

    for market in markets:
        market_id = market.get("id") or market.get("conditionId") or market.get("slug")
        if not market_id:
            continue
        rows.append({
            "market_id": market_id,
            "question": market.get("question") or market.get("title") or "",
            "price": _extract_snapshot_price(market),
            "liquidity": market.get("liquidity"),
            "volume24hr": market.get("volume24hr"),
            "timestamp": now,
        })

    df = pd.DataFrame(rows)
    if PRICE_HISTORY_PATH.exists():
        old = pd.read_csv(PRICE_HISTORY_PATH)
        df = pd.concat([old, df], ignore_index=True)
        # Keep file manageable. Last 20,000 rows is plenty for this local scanner.
        df = df.tail(20000)

    df.to_csv(PRICE_HISTORY_PATH, index=False)
    return PRICE_HISTORY_PATH
