# Outbox: pago → ledger + wallet

Cuando una orden pasa a `SUCCESS` hay que avisarles a ledger, wallet, notificaciones, analytics... Si actualizás el estado y después publicás en el broker, cualquiera de las dos cosas puede fallar sola (*dual write*).

La solución: el cambio de estado y el evento se guardan **en la misma transacción** (tabla `outbox`). Un *relay* publica lo pendiente. Los consumidores son **idempotentes** (dedup por `payment_order_id`), porque el relay puede publicar dos veces.

**Ejemplo real:** Postgres + Debezium (CDC) leyendo la outbox, o un relay propio con `SELECT ... FOR UPDATE SKIP LOCKED`.

```
Executor ─► BEGIN
              UPDATE payment_orders SET status='SUCCESS'
              INSERT outbox ('pago.exitoso', po_1)
            COMMIT
relay    ─► outbox pendientes ─► broker ─┬─► Ledger  (dedup por tx id)  ─► ledger_updated = true
                                         └─► Wallet  (dedup por tx id)  ─► wallet_updated = true
```

Este es el modelo **pub/sub** (varios receptores para el mismo mensaje): un pago dispara varios efectos independientes, y si wallet está caída, ledger igual avanza; wallet se pone al día cuando vuelve.
