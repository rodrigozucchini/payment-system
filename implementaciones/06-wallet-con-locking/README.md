# Wallet con locking

La wallet guarda el saldo de cada vendedor para responder rápido "¿cuánto tengo?" sin sumar todo el ledger. Como varios procesos la modifican a la vez (cobros, refunds, payouts), cada cambio tiene que ser **atómico**.

**Ejemplo real:** el balance de una cuenta de Stripe Connect, la "cuenta" de Mercado Pago de un vendedor.

Tres formas de hacerlo bien:

```sql
-- 1. Update atómico con condición (la más simple)
UPDATE wallets SET saldo = saldo - 8000
WHERE seller_id = 'juan' AND saldo >= 8000;          -- 0 filas => saldo insuficiente

-- 2. Lock pesimista
BEGIN;
SELECT saldo FROM wallets WHERE seller_id = 'juan' FOR UPDATE;   -- los demás esperan
UPDATE wallets SET saldo = ... ;
COMMIT;

-- 3. Optimistic locking
UPDATE wallets SET saldo = 2000, version = 8
WHERE seller_id = 'juan' AND version = 7;            -- 0 filas => alguien cambió: releer y reintentar
```

Además se separan dos saldos:
- **pendiente**: cobrado, pero en período de retención (por chargebacks, entregas, etc.).
- **disponible**: lo que se puede pagar en un payout.

Lo que NO hay que hacer es "leer saldo en la app, restar en la app, escribir el resultado" sin lock: ver [errores/04-race-condition-saldo](../../errores/04-race-condition-saldo).
