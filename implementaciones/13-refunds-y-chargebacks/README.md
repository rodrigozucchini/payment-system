# Refunds y chargebacks

**Refund**: lo inicia el comercio ("te devuelvo la plata"). Puede ser total o parcial, y puede haber varios parciales sobre el mismo cobro.

**Chargeback (contracargo)**: lo inicia el **banco del comprador** ("no reconozco esta compra", "nunca llegó"). La plata se te descuenta de entrada, más un fee (ej. USD 15). Tenés unos días para presentar evidencia (*representment*); si ganás, vuelve.

**Ejemplo real:** `POST /v1/refunds` y el objeto `Dispute` de Stripe; "reclamos" y "contracargos" de Mercado Pago.

```
Cobro $100 (SUCCESS)
  ├── refund $30 ─► PARTIALLY_REFUNDED (refundado 30)
  ├── refund $70 ─► REFUNDED (refundado 100)
  └── refund $1  ─► ✗ rechazado: supera lo cobrado

Cobro $50 ─► chargeback ─► DISPUTED (-$50 -$15 fee) ─┬─ ganamos ─► WON  (+$50)
                                                     └─ perdemos ─► LOST
```

Reglas:
- Un refund es una **operación nueva** con su propia idempotency key, no un "deshacer". En el ledger son asientos nuevos (inversos).
- `total_refundado + nuevo <= capturado`, validado **con lock** sobre el cobro (si no, dos refunds concurrentes se pasan).
- ¿Quién paga? Si el vendedor ya cobró (payout), su saldo puede quedar **negativo**: hay que decidir si se descuenta de futuros cobros. Por eso existe el período de retención.
- Los fees del PSP muchas veces **no se devuelven** con el refund.
