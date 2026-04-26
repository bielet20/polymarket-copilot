# Polymarket Copiloto Pro v2

Copiloto de analisis para Polymarket en modo seguro. Escanea mercados, calcula edge conservador, detecta movimiento local de precio, prioriza mercados informativos y registra senales.

## Cambios v2

- Corrige bug de `movement` usado fuera de contexto.
- Corrige bug de `m` usado antes del loop.
- Anade `movement` y `movement_pct` a las senales.
- Guarda `data/price_history.csv` para detectar caidas/subidas tras varios scans.
- Penaliza deportes sin modelo dedicado.
- Prioriza politica, macro/economia y crypto.
- Mantiene trading real desactivado.

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Ejecutar

```bash
python main.py scan
```

Despues de varios scans, el detector de movimiento empieza a aportar valor porque necesita historico local.

## Ver reporte

```bash
python main.py report
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
- Este proyecto no ejecuta ordenes reales.
