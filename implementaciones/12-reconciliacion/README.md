# Reconciliación

Aunque todo lo anterior esté bien hecho, **algo se va a desincronizar**: un webhook que nunca llegó, un refund que alguien hizo a mano desde el dashboard del PSP, un fee que cambió, un settlement que vino incompleto. La reconciliación es la red de seguridad.

Cada día el PSP manda un **archivo de settlement** (CSV/SFTP/API) con lo que efectivamente procesó. Se compara contra nuestro sistema y contra el extracto del banco:

```
Nuestros payment_orders ─┐
                         ├─► match por psp_id / payment_order_id ─► diferencias ─► clasificar
Settlement del PSP ──────┘                                                     ├─ auto-ajustable
                                                                               ├─ manual con procedimiento
Ledger ◄──► Wallet  (consistencia interna: ¿saldo wallet = saldo ledger?)       └─ a investigar
Settlement ◄──► Banco  (¿llegó la plata que el PSP dice que mandó?)
```

**Ejemplo real:** los *Balance/Payout reconciliation reports* de Stripe, *Settlement details report* de Adyen.

Tipos de diferencia típicas:
- **Falta en nuestro sistema**: el PSP cobró pero nosotros tenemos `FAILED`/`UNKNOWN` (timeout, webhook perdido).
- **Falta en el PSP**: tenemos `SUCCESS` pero el PSP no lo liquidó (bug, estado mal seteado).
- **Monto distinto**: captura parcial, fees, conversión de moneda.
- **Estado distinto**: refund o chargeback que no nos enteramos.
- **Interna**: wallet ≠ suma del ledger.

Se clasifican: las conocidas se ajustan solas (con asiento en el ledger, nunca editando), las conocidas pero delicadas van a finanzas con un procedimiento, y las desconocidas se investigan. Todo con alerta y con métricas (cantidad y monto de diferencias por día).
