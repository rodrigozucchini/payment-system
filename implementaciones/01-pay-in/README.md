# Pay-in de punta a punta

El camino feliz completo: el usuario paga un carrito con dos vendedores, el **Payment Service** guarda el evento, el **Executor** cobra cada orden contra el PSP, y después se actualizan **ledger** y **wallet**.

**Ejemplo real:** Amazon, Mercado Libre o cualquier marketplace usando Stripe/Adyen por detrás.

```
POST /payments ─► Payment Service ─► guarda event + orders (NOT_STARTED)
                       │
                       └─► Executor ─► order: EXECUTING ─► PSP.charge(id=payment_order_id)
                                                              │
                          order: SUCCESS ◄────────────────────┘
                              ├─► Wallet: saldo vendedor += monto - comisión
                              └─► Ledger: asientos de doble entrada
```

Fijate en tres cosas:
- La orden se guarda **antes** de llamar al PSP (si nos caemos en el medio, sabemos que hay algo en curso).
- Al PSP le mandamos **nuestro** `payment_order_id` como idempotency key.
- `ledger_updated` y `wallet_updated` dejan rastro de qué pasos se completaron, para poder retomar.
