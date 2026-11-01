# Idempotency key en la API

El cliente genera un UUID por **intento de pago** (no por request) y lo manda en el header `Idempotency-Key`. Si el mismo request llega dos veces (doble click, retry del front, reintento del load balancer), el servidor devuelve la **misma respuesta** que la primera vez sin volver a cobrar.

**Ejemplo real:** el header `Idempotency-Key` de Stripe, `X-Idempotency-Key` de Mercado Pago, `Idempotency-Key` de Adyen.

```
POST /payments  Idempotency-Key: abc  ─► INSERT key (UNIQUE) ✓ ─► cobrar ─► guardar respuesta ─► 200
POST /payments  Idempotency-Key: abc  ─► INSERT key ✗ (ya existe) ─► devolver respuesta guardada ─► 200
POST /payments  Idempotency-Key: abc  ─► ...pero la primera todavía está procesando ─► 409 Conflict
POST /payments  Idempotency-Key: abc  ─► ...con OTRO body ─► 422 (misma key, distinto pedido)
```

Detalles que importan:
- La deduplicación la hace la **DB** con una constraint `UNIQUE`, no un `if` en memoria (dos requests simultáneos pasan los dos el `if`).
- Se guarda un **hash del body** para detectar que usaron la misma key para otra cosa.
- Mientras el primero está en curso, el segundo recibe `409` con `Retry-After`, no un segundo cobro.
- Las keys se guardan por un tiempo (Stripe: 24 h) y después se pueden limpiar.
- La idempotencia se repite en **cada salto**: cliente → nosotros (Idempotency-Key) y nosotros → PSP (payment_order_id).
