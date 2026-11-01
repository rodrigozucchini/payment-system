# Pagos pendientes y estado UNKNOWN

Hay dos situaciones donde no sabés cómo terminó un pago:

**PENDING (sabés que está en curso):** el PSP te dijo "procesando". Pasa con 3DS (el usuario tiene que confirmar en la app del banco), revisión manual de fraude, transferencias, Pix/Boleto/efectivo. Puede tardar minutos u horas (o días).
→ Mostrar "pendiente" al usuario, esperar webhook, y si no llega, **polling** al PSP. Avisar por email cuando se resuelva. Poner un vencimiento.

**UNKNOWN (no sabés nada):** mandaste el request y hubo timeout o se cortó la conexión. El PSP pudo haber cobrado o no.
→ **No es un fallo.** Un job consulta al PSP por el `payment_order_id`:
- Si el PSP lo tiene → usar ese resultado.
- Si el PSP no lo tiene → re-ejecutar con la **misma** idempotency key (si llegó tarde, el PSP deduplica).

**Ejemplo real:** `GET /v1/payment_intents/:id` en Stripe, `GET /v1/payments/search?external_reference=` en Mercado Pago.

```
            timeout
EXECUTING ──────────► UNKNOWN ──► job cada N min ──► PSP.get(po_1)
                                                      ├─ succeeded ─► SUCCESS
                                                      ├─ failed    ─► FAILED
                                                      └─ not_found ─► reintentar charge(po_1)
```

El mismo job sirve de **barredora**: cualquier orden en `EXECUTING`/`UNKNOWN`/`PENDING` por más de X minutos se consulta, y si pasa demasiado tiempo se alerta.
