import argparse
from rich.console import Console
from rich.table import Table
from src.config import load_config
from src.market_data import fetch_active_markets
from src.strategy import score_markets
from src.storage import save_signals, load_signals, save_price_snapshot
from src.trading import place_buy_order, get_balance, get_token_id

console = Console()


def cmd_scan():
    cfg = load_config()
    console.print("[bold]Escaneando mercados activos...[/bold]")
    markets = fetch_active_markets(limit=250)
    save_price_snapshot(markets)
    signals = score_markets(markets, cfg)
    out = save_signals(signals)

    console.print(f"[green]Señales guardadas en:[/green] {out}")
    console.print("")
    console.print("[bold]Top señales[/bold]")

    for signal in signals[:12]:
        action = signal["action"]
        color = "green" if action == "COMPRAR_YES" else "cyan" if action == "VIGILAR" else "yellow"
        console.print(
            f"[{color}]{action}[/{color}] | "
            f"{signal['question'][:80]} | "
            f"cat={signal['category']} | "
            f"precio={signal['market_price']:.2f} | "
            f"prob_modelo={signal['model_probability']:.2f} | "
            f"edge={signal['edge']:.2%} | "
            f"mov={signal['movement']}({signal['movement_pct']:.1%}) | "
            f"stake={signal['recommended_stake_usdc']:.2f} USDC | "
            f"score={signal['score']:.1f} | "
            f"reasons={signal['reasons']}"
        )


def cmd_report():
    df = load_signals()
    if df.empty:
        console.print("[yellow]Aún no hay señales. Ejecuta: python main.py scan[/yellow]")
        return
    cols = [
        "created_at_utc", "action", "category", "question", "market_price",
        "model_probability", "edge", "movement", "movement_pct",
        "recommended_stake_usdc", "score", "reasons"
    ]
    cols = [c for c in cols if c in df.columns]
    console.print(df[cols].tail(30).to_string(index=False))


def cmd_trade(market_slug: str, price: float, size: float, confirm: bool = False):
    console.print(f"[bold]Ejecutando orden BUY[/bold]")
    console.print(f"  Market: {market_slug}")
    console.print(f"  Precio: {price}")
    console.print(f"  Tamaño: {size} USDC")
    console.print(f"  Costo: {price * size:.2f} USDC")

    token_id = get_token_id(market_slug)
    if not token_id:
        console.print("[red]Error: No se encontró el token_id para este mercado[/red]")
        return

    console.print(f"  Token ID: {token_id}")

    result = place_buy_order(token_id, price, size, confirm=confirm)

    if result["status"] == "preview":
        console.print(f"\n[yellow]PREVIEW - No se ejecutó[/yellow]")
        console.print(f"Usa --confirm para ejecutar realmente")
    else:
        console.print(f"\n[green]Orden enviada:[/green] {result}")


def cmd_balance():
    balance = get_balance()
    console.print(f"[bold]Balance USDC:[/bold] {balance:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Polymarket Copiloto Pro v2")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("scan", help="Escanear mercados y generar señales")
    sub.add_parser("report", help="Ver últimas señales")
    sub.add_parser("balance", help="Ver balance USDC")

    trade_parser = sub.add_parser("trade", help="Ejecutar orden BUY")
    trade_parser.add_argument("--market", required=True, help="Market slug de Polymarket")
    trade_parser.add_argument("--price", type=float, required=True, help="Precio (0.01 - 0.99)")
    trade_parser.add_argument("--size", type=float, required=True, help="Tamaño en USDC")
    trade_parser.add_argument("--confirm", action="store_true", help="Confirmar ejecución real")

    args = parser.parse_args()

    if args.cmd == "scan":
        cmd_scan()
    elif args.cmd == "report":
        cmd_report()
    elif args.cmd == "balance":
        cmd_balance()
    elif args.cmd == "trade":
        cmd_trade(args.market, args.price, args.size, args.confirm)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()