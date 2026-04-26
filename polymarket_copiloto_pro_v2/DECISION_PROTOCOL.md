# Protocolo profesional de decision v2

## Regla 0: Control humano

El copiloto propone; tu decides. No se ejecutan apuestas automaticas.

## Regla 1: Edge minimo

Solo considerar `COMPRAR_YES` cuando:

```text
edge >= 8%
stake > 0
reasons = ok
```

## Regla 2: VIGILAR no es apuesta

`VIGILAR` significa: mirar el mercado, buscar informacion y esperar mejor precio.

## Regla 3: Prioridad

1. Politica y macro.
2. Crypto con liquidez.
3. Other solo si entiendes la resolucion.
4. Deportes bloqueados salvo modelo dedicado.

## Regla 4: Detector de movimiento

- `drop` / `sharp_drop`: posible value, pero puede ser informacion negativa.
- `momentum` / `strong_momentum`: posible seguimiento, pero evita perseguir subidas sin noticia.
- Movimiento solo es util con volumen suficiente.

## Regla 5: Staking

- Edge < 8%: 0 USDC.
- Edge 8-12%: 0.5% bankroll.
- Edge 12-18%: 1% bankroll.
- Edge >18%: 1.5% bankroll.

## Regla 6: No deportes por ahora

Tu historico inicial mostraba mal rendimiento en basketball y casi break-even en tennis. La v2 bloquea deportes generales para no inventar edge.

## Regla 7: Revision semanal

Revisa:

- ROI por categoria.
- Winrate por categoria.
- Promedio de edge de `COMPRAR_YES`.
- Si los `VIGILAR` terminaron siendo mejores entradas.
- Drawdown maximo.
