# Retries con backoff y Dead Letter Queue

No todos los errores son iguales. Antes de reintentar hay que **clasificar**:

| Tipo | Ejemplos | Qué hacer |
|---|---|---|
| **Reintentable** | timeout, 500/502/503, 429 rate limit, error de conexión | Retry con backoff exponencial + jitter, **misma idempotency key**. |
| **Terminal** | `card_declined`, `insufficient_funds`, `invalid_card`, `fraudulent`, 400 | No reintentar. `FAILED` y avisar al usuario. |
| **Desconocido** | timeout después de mandar el request | `UNKNOWN`: consultar el estado antes (ver [10](../10-pendientes-y-unknown)). |

**Ejemplo real:** Stripe recomienda reintentar solo errores de red/5xx con la misma `Idempotency-Key`; los SDKs ya traen backoff.

```
intento 1 ─✗ 503─► espera ~1s ─► intento 2 ─✗ 503─► ~2s ─► intento 3 ─✗─► ~4s ─► ... ─► máx N ─► DLQ
intento 1 ─✗ card_declined ─► FAILED (sin retry)
```

- **Backoff exponencial**: `base * 2^intento`, con tope.
- **Jitter**: un random encima, para que mil pagos no reintenten todos en el mismo milisegundo.
- **Retry-After**: si el PSP lo manda, respetarlo.
- **DLQ**: lo que agotó los intentos va a una cola aparte con todo el contexto, con alerta, para que alguien lo mire. Nunca se descarta en silencio.
