# Máquina de estados de una orden de pago

El estado de un pago no se "setea": **transiciona**. Hay una tabla de transiciones válidas y todo cambio pasa por ella. Así un webhook viejo, un bug o un retry no pueden llevar un pago a un estado imposible.

**Ejemplo real:** el `PaymentIntent` de Stripe (`requires_payment_method → processing → succeeded`), los estados de Adyen, cualquier tabla `payment_orders` seria.

```
NOT_STARTED ─► EXECUTING ─┬─► SUCCESS ─► PARTIALLY_REFUNDED ─► REFUNDED
                          │      └─────► CHARGEBACK
                          ├─► PENDING ─► SUCCESS | FAILED
                          ├─► UNKNOWN ─► SUCCESS | FAILED   (después de consultar al PSP)
                          └─► FAILED   (terminal)
```

En la DB, la transición se hace con un **compare-and-set**, para que dos procesos no transicionen a la vez desde el mismo estado:

```sql
UPDATE payment_orders SET status = 'SUCCESS', version = version + 1
WHERE payment_order_id = 'po_1' AND status = 'EXECUTING';
-- 0 filas afectadas => otro proceso ya la movió: no hacer nada (o releer)
```
