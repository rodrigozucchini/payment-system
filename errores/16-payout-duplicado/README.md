# Payout duplicado o sin saldo

El pay-out es plata que **sale** y casi nunca vuelve: si le pagás dos veces a un vendedor, recuperarlo es un trámite (o imposible). Formas típicas de equivocarse:
- El cron corre en **dos instancias** a la vez (dos pods, un deploy en el medio).
- El job falla a la mitad y se relanza desde el principio, re-pagando a los que ya se pagaron.
- Se crea el payout, se llama al banco, y **después** se debita el saldo (si se cae en el medio, el saldo sigue ahí para el próximo payout).
- Se paga el **saldo total** en vez del **disponible** (incluye cobros recientes que todavía pueden tener refund o chargeback).
- Se ignora que una transferencia rebotó, o se reintenta con un id nuevo.

```
❌ for vendedor: banco.transferir(saldo_total)   → corre dos veces = paga dos veces
✅ for vendedor:
     BEGIN; INSERT payout (id = 'payout:juan:2026-11-01' UNIQUE); saldo -= disponible; COMMIT;
     banco.transferir(id = 'payout:juan:2026-11-01')    ← idempotente también del lado del banco
```

**Fix:** id determinístico por vendedor y período, débito del saldo en la misma transacción que crea el payout, solo saldo disponible, lock para que corra una sola instancia del job. Ver [implementaciones/14-payouts](../../implementaciones/14-payouts).
