# Reintentar todo

Un `try/except: retry` genérico alrededor del cobro. Funciona para un timeout, pero:
- **`card_declined`, `insufficient_funds`, `expired_card`, `fraudulent`**: reintentar no los arregla. Cada intento puede tener costo, y muchos rechazos seguidos hacen que el emisor bloquee la tarjeta o que las redes te multen / te pongan en programas de monitoreo (*excessive retries*). Visa y Mastercard limitan cuántas veces se puede reintentar una tarjeta rechazada.
- **400 / datos inválidos**: el mismo request va a fallar siempre.
- **Retries sin backoff**: si el PSP está caído, mil workers reintentando al toque lo terminan de tirar (*retry storm*) y te rate-limitea.
- **Retries en varias capas**: el SDK reintenta 3, tu código 3, la cola 3 → 27 intentos.
- **Reintentar con otro PSP ante un timeout**: posible doble cobro (ver [18-multi-psp](../../implementaciones/18-multi-psp)).

```
❌ for i in range(5): try: charge() except: continue
✅ error reintentable (timeout*, 5xx, 429, red) → backoff + jitter + misma key + tope → DLQ
   error terminal (rechazo, fraude, 4xx)        → FAILED, avisar al usuario, no reintentar
   * timeout → primero consultar (UNKNOWN)
```

**Fix:** clasificar errores, backoff exponencial con jitter, tope de intentos, retries en **una sola capa**, respetar `Retry-After`. En suscripciones, reintentos espaciados en días con lógica de *dunning*. Ver [implementaciones/09-retry-y-dlq](../../implementaciones/09-retry-y-dlq).
