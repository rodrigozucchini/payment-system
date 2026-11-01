# Leer el estado del pago desde una réplica

Para descargar al primario, las lecturas van a réplicas. Pero la replicación tiene **lag** (milisegundos, a veces segundos o minutos bajo carga). Justo después de un pago:

```
t0  primario: po_1 = SUCCESS
t1  GET /payments/po_1 ─► réplica (lag): po_1 = EXECUTING ─► front: "tu pago no se completó, reintentá"
t2  usuario paga de nuevo ─► segundo cobro (o se le muestra un error a alguien que ya pagó)
```

Otros casos: el job de payouts lee el saldo de una réplica atrasada y paga plata que ya se debitó; la validación de refund lee lo refundado de una réplica y deja pasar uno de más.

**Fix:**
- Lecturas que deciden algo con plata (saldo, estado del pago, lo refundado) → **siempre al primario**. Las réplicas, para reportes y failover.
- *Read-your-writes*: después de escribir, ese usuario lee del primario por unos segundos (o se pasa la posición del WAL/LSN).
- O una DB con consenso (CockroachDB, Spanner, Yugabyte) donde las lecturas son consistentes.
- Y en cualquier caso, la idempotency key protege del cobro doble aunque el usuario reintente.
