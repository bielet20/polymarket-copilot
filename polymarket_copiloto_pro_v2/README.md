# Polymarket Copiloto Pro v2

Copiloto de analisis para Polymarket en modo seguro. Escanea mercados, calcula edge conservador, detecta movimiento local de precio, prioriza mercados informativos y registra senales.

## Cambios v3

- Anade integracion con `py-clob-client` para trading real.
- Nuevo comando `trade` para ejecutar ordenes BUY desde senales.
- Nuevo comando `balance` para ver balance USDC.

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Configurar trading

Edita `.env` y anade tus credenciales de Polymarket:

```env
POLYMARKET_PRIVATE_KEY=tu_clave_privada_wallet
POLYMARKET_API_KEY=tu_api_key
POLYMARKET_API_SECRET=tu_api_secret
POLYMARKET_API_PASSPHRASE=tu_api_passphrase
POLYMARKET_FUNDER_ADDRESS=tu_direccion_usdc
```

## Ejecutar

```bash
python main.py scan
python main.py report
python main.py balance
```

## Trading real

Despues de un scan, puedes ejecutar una orden:

```bash
python main.py trade --market "will-trump-win-2024" --price 0.55 --size 5
```

Para ejecutar realmente (sin --confirm es solo preview):

```bash
python main.py trade --market "will-trump-win-2024" --price 0.55 --size 5 --confirm
```

## Interpretacion

- `COMPRAR_YES`: candidato con edge minimo, filtros superados y stake positivo.
- `VIGILAR`: posible oportunidad, pero sin edge suficiente para apostar.
- `NO_ENTRAR`: descartar por filtros, categoria, precio extremo, volumen o edge bajo.

## Reglas de operacion recomendadas

- No operar deportes hasta tener modelo dedicado.
- No apostar mercados `VIGILAR`.
- Confirmar manualmente cualquier `COMPRAR_YES`.
- Revisar noticias/contexto antes de entrar.
- Mantener stake pequeno: v2 usa 0.5%-1.5% segun edge.

## Seguridad

- No incluyas tu `.env` en repositorios.
- No compartas claves privadas.
- Usa --confirm solo cuando quieras ejecutar realmente.