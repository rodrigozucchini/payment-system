# Payouts

El pay-out le paga a cada vendedor lo que la plataforma le debe. Suele ser un **job batch** (diario/semanal/mensual) que:

1. Toma el **saldo disponible** de cada vendedor (no el total: lo cobrado hace menos de N días queda retenido por si hay refunds/chargebacks).
2. Descarta montos debajo de un mínimo, cuentas sin KYC aprobado, o vendedores bloqueados.
3. Crea un `payout` con id **determinístico** (`payout:{seller}:{período}`) y **en la misma transacción** debita el saldo.
4. Lo manda al banco / proveedor de payouts (Tipalti, Stripe Connect, Payoneer, Wise) con ese id como idempotency key.
5. Espera la confirmación (las transferencias pueden rebotar: cuenta cerrada, CBU/IBAN inválido → se devuelve el saldo).

**Ejemplo real:** Amazon paga a sus sellers cada 14 días, Uber a sus conductores semanalmente, Stripe Connect con `payout_schedule`.

```
wallet ─► disponible = cobrado hace > 7 días - refunds - chargebacks
       ─► payout:juan:2026-11-01 (UNIQUE) + debitar saldo  (misma tx)
       ─► banco.transfer(id=payout:juan:2026-11-01)
       ─► PAID  |  FAILED ─► acreditar saldo de vuelta
```

Si el job se corre dos veces (deploy, retry, dos instancias del cron), el id determinístico hace que el segundo no pague nada.
