from __future__ import annotations

from math import log1p
from typing import Any


def safe_float(x, default=0.0):
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


def classify_category(market: dict[str, Any]) -> str:
    text = " ".join(
        str(market.get(k, ""))
        for k in ["question", "title", "description", "category", "slug"]
    ).lower()

    if any(x in text for x in [
        "nba", "basketball", "lakers", "warriors", "celtics",
        "timberwolves", "knicks", "bucks", "heat", "76ers"
    ]):
        return "basketball"
    if any(x in text for x in [
        "tennis", "atp", "wta", "madrid open", "roland garros", "wimbledon",
        "us open", "australian open"
    ]):
        return "tennis"
    if any(x in text for x in [
        "election", "president", "trump", "biden", "congress", "senate",
        "politics", "iran", "ceasefire", "diplomatic", "peace deal"
    ]):
        return "politics"
    if any(x in text for x in [
        "bitcoin", "ethereum", "crypto", "solana", "btc", "eth", "xrp"
    ]):
        return "crypto"
    if any(x in text for x in [
        "fed", "inflation", "cpi", "rates", "economy", "gdp", "interest rates",
        "unemployment", "recession"
    ]):
        return "economics"
    if any(x in text for x in [
        "fifa", "world cup", "champions league", "mlb", "braves", "phillies",
        "fiorentina", "football", "soccer", "lol", "lck", "esports"
    ]):
        return "sports_other"
    return "other"


def extract_price(market: dict[str, Any]) -> float:
    for key in ["lastTradePrice", "bestAsk", "bestBid"]:
        p = safe_float(market.get(key), None)
        if p is not None and 0 < p < 1:
            return p

    prices = market.get("outcomePrices") or []
    if isinstance(prices, str):
        try:
            import json
            prices = json.loads(prices)
        except Exception:
            prices = []

    if isinstance(prices, list) and prices:
        p = safe_float(prices[0], 0.5)
        if 0 < p < 1:
            return p

    return 0.5


def category_base_adjustment(category: str) -> float:
    """
    Conservative base adjustment. This is not a prediction model.
    It only reflects your historical preference for non-sports/informational markets.
    """
    if category in ["politics", "economics"]:
        return 0.035
    if category == "crypto":
        return 0.025
    if category == "other":
        return 0.015
    if category == "tennis":
        return -0.015
    if category in ["basketball", "sports_other"]:
        return -0.035
    return 0.0


def liquidity_adjustment(liquidity: float, volume24h: float) -> float:
    adj = 0.0
    if liquidity > 5000:
        adj += 0.010
    if liquidity > 25000:
        adj += 0.005
    if volume24h > 5000:
        adj += 0.010
    if volume24h > 25000:
        adj += 0.005
    return adj


def detect_movement(market_id: Any) -> tuple[str, float]:
    """
    Uses local price_history.csv. Needs several scans before it becomes useful.
    Returns: (movement_label, relative_change)
    """
    try:
        import pandas as pd
        from src.storage import PRICE_HISTORY_PATH
    except Exception:
        return "neutral", 0.0

    if not market_id or not PRICE_HISTORY_PATH.exists():
        return "neutral", 0.0

    try:
        df = pd.read_csv(PRICE_HISTORY_PATH)
    except Exception:
        return "neutral", 0.0

    if df.empty or "market_id" not in df.columns or "price" not in df.columns:
        return "neutral", 0.0

    market_df = df[df["market_id"].astype(str) == str(market_id)].copy()
    if len(market_df) < 4:
        return "neutral", 0.0

    market_df = market_df.sort_values("timestamp").tail(6)
    old_price = safe_float(market_df.iloc[0]["price"], 0.0)
    new_price = safe_float(market_df.iloc[-1]["price"], 0.0)

    if old_price <= 0:
        return "neutral", 0.0

    change = (new_price - old_price) / old_price

    if change <= -0.12:
        return "sharp_drop", change
    if change <= -0.06:
        return "drop", change
    if change >= 0.12:
        return "strong_momentum", change
    if change >= 0.06:
        return "momentum", change
    return "neutral", change


def movement_adjustment(movement: str, volume24h: float) -> float:
    """
    Movement only matters when there is enough volume.
    A drop can be value, but it can also be information against you, so keep boosts small.
    """
    if volume24h < 1000:
        return 0.0
    if movement == "sharp_drop":
        return 0.020
    if movement == "drop":
        return 0.010
    if movement == "strong_momentum":
        return 0.015
    if movement == "momentum":
        return 0.008
    return 0.0


def estimate_probability(
    market: dict[str, Any],
    category: str,
    price: float,
    movement: str = "neutral",
) -> float:
    liquidity = safe_float(market.get("liquidity"), 0)
    volume24h = safe_float(market.get("volume24hr"), 0)

    adjustment = 0.0
    adjustment += category_base_adjustment(category)
    adjustment += liquidity_adjustment(liquidity, volume24h)
    adjustment += movement_adjustment(movement, volume24h)

    # Extreme prices require much stronger external evidence.
    if price < 0.12 or price > 0.88:
        adjustment -= 0.025
    elif price < 0.18 or price > 0.82:
        adjustment -= 0.010

    prob = price + adjustment
    return max(0.01, min(0.99, prob))


def stake_from_edge(edge: float, bankroll: float, max_stake_pct: float) -> float:
    if edge < 0.08:
        pct = 0.0
    elif edge < 0.12:
        pct = 0.005
    elif edge < 0.18:
        pct = 0.010
    else:
        pct = 0.015
    return min(bankroll * pct, bankroll * max_stake_pct)


def category_score(category: str) -> int:
    if category in ["politics", "economics"]:
        return 25
    if category == "crypto":
        return 18
    if category == "other":
        return 8
    if category == "tennis":
        return -8
    if category in ["basketball", "sports_other"]:
        return -15
    return 0


def score_markets(markets: list[dict[str, Any]], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    bankroll = safe_float(cfg.get("bankroll_usdc"), 1000)
    min_edge = safe_float(cfg.get("risk", {}).get("min_edge"), 0.08)
    max_stake_pct = safe_float(cfg.get("risk", {}).get("max_stake_pct"), 0.03)

    filters = cfg.get("filters", {})
    avoid = set(x.lower() for x in filters.get("avoid_categories", []))

    signals = []

    for market in markets:
        market_id = market.get("id") or market.get("conditionId") or market.get("slug")
        question = market.get("question") or market.get("title") or "Untitled market"
        category = classify_category(market)
        liquidity = safe_float(market.get("liquidity"), 0)
        volume24h = safe_float(market.get("volume24hr"), 0)
        price = extract_price(market)
        movement, movement_pct = detect_movement(market_id)

        model_prob = estimate_probability(market, category, price, movement)
        edge = model_prob - price

        passes = True
        reasons = []

        if category in avoid:
            passes = False
            reasons.append("categoria_bloqueada")
        if category in ["basketball", "sports_other"]:
            passes = False
            reasons.append("deportes_sin_modelo_dedicado")
        if liquidity < safe_float(filters.get("min_liquidity"), 1000):
            passes = False
            reasons.append("liquidez_baja")
        if volume24h < safe_float(filters.get("min_volume_24h"), 500):
            passes = False
            reasons.append("volumen_bajo")
        if price < safe_float(filters.get("min_price"), 0.08) or price > safe_float(filters.get("max_price"), 0.92):
            passes = False
            reasons.append("precio_extremo")
        if edge < min_edge:
            passes = False
            reasons.append("edge_insuficiente")

        stake = stake_from_edge(edge, bankroll, max_stake_pct) if passes else 0.0

        liquidity_score = min(20, log1p(max(liquidity, 0)))
        volume_score = min(20, log1p(max(volume24h, 0)))
        edge_score = max(0, edge * 400)
        movement_score = 8 if movement in ["drop", "sharp_drop", "momentum", "strong_momentum"] else 0
        score = liquidity_score + volume_score + edge_score + category_score(category) + movement_score

        if passes and stake > 0 and edge >= min_edge:
            action = "COMPRAR_YES"
        elif edge >= 0.05 and category not in ["basketball", "sports_other"]:
            action = "VIGILAR"
        else:
            action = "NO_ENTRAR"

        signals.append({
            "market_id": market_id,
            "question": question,
            "category": category,
            "action": action,
            "market_price": round(price, 4),
            "model_probability": round(model_prob, 4),
            "edge": round(edge, 4),
            "liquidity": round(liquidity, 2),
            "volume24h": round(volume24h, 2),
            "movement": movement,
            "movement_pct": round(movement_pct, 4),
            "recommended_stake_usdc": round(stake, 2),
            "score": round(score, 2),
            "reasons": ",".join(reasons) if reasons else "ok",
            "url": market.get("slug") or market.get("marketSlug") or "",
        })

    return sorted(signals, key=lambda x: x["score"], reverse=True)
