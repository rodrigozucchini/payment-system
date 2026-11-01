# Ledger de doble entrada

Cada movimiento de plata se registra como una **transacción** con al menos dos asientos (*entries*): débitos y créditos que **suman lo mismo**. Si una transacción no balancea, se rechaza entera. El saldo de cualquier cuenta se **deriva** sumando sus asientos.

**Ejemplo real:** el ledger interno de Stripe, Square o Uber; TigerBeetle, Formance, Modern Treasury como ledgers listos.

```
tx_1 (cobro $100)       DEBE                     HABER
                        psp_por_cobrar   100     vendedor:juan     97
                                                 ingresos:comision  3
                        ──────────────────────────────────────────────
                        100              =      100   ✅

tx_2 (refund de tx_1)   vendedor:juan     97     psp_por_cobrar   100
                        ingresos:comision  3
```

Reglas:
- **Append-only**: nunca `UPDATE` ni `DELETE`. Un error se corrige con una transacción de reversa.
- **Todas las patas o ninguna**: los asientos de una transacción se insertan en la misma transacción de DB.
- **Idempotente**: cada transacción tiene un id externo (ej. `payment_order_id`); si llega dos veces, no se duplica.
- Convención de signo según el tipo de cuenta: en un **activo** (banco, por cobrar) el débito suma; en un **pasivo** (lo que le debemos al vendedor) o **ingreso**, el crédito suma.
