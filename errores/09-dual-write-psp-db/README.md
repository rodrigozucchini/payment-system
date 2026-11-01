# Dual write: PSP y DB por separado

Llamar al PSP y guardar en tu DB son dos sistemas distintos: no hay transacción que cubra a los dos. Si el proceso se cae entre una cosa y la otra, quedan desincronizados.

```
❌ PSP.charge() ✓ ─► 💥 (crash/deploy/OOM) ─► INSERT pago   nunca pasa
   → al cliente se le cobró, nosotros no tenemos ningún registro. Nadie lo va a buscar.

✅ INSERT orden (EXECUTING, id=po_1) ─► PSP.charge(id=po_1) ✓ ─► 💥
   → queda una orden EXECUTING colgada ─► la barredora consulta PSP.get(po_1) ─► SUCCESS
```

Lo mismo pasa al revés (guardar `SUCCESS` y después llamar al PSP), y entre la DB y el broker (ver la outbox).

**Fix:**
- **Primero persistir la intención** (orden en `EXECUTING` con el id que va a viajar al PSP), después llamar.
- Job barredora que retoma órdenes colgadas consultando al PSP por ese id.
- Outbox para los eventos posteriores (ledger, wallet).
- Reconciliación diaria para lo que se escape.
