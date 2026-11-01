# No tener idempotency key (doble click)

El usuario aprieta "Pagar", la página tarda, aprieta otra vez. O el front reintenta por un timeout. O el load balancer reenvía el request. Sin idempotencia, cada request es un cobro nuevo.

```
❌ POST /payments (click 1) ─► cobrar $50
   POST /payments (click 2) ─► cobrar $50     → cobrado $100
✅ POST /payments  Idempotency-Key: k1 ─► cobrar $50
   POST /payments  Idempotency-Key: k1 ─► ya existe ─► misma respuesta   → cobrado $50
```

Deshabilitar el botón en el front ayuda pero **no alcanza** (refresh, dos pestañas, reintentos de red).

Y ojo: un `if existe: return` en memoria tampoco alcanza. Dos requests simultáneos pasan los dos el `if` antes de que cualquiera escriba. La deduplicación tiene que ser una **constraint `UNIQUE` en la DB**.

**Fix:** el cliente genera la key una vez por intento de pago, el servidor la guarda con `UNIQUE`, y el mismo id viaja al PSP. Ver [implementaciones/04-idempotency-key](../../implementaciones/04-idempotency-key).
