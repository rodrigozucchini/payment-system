# Refund mayor a lo cobrado

Distintas formas de devolver más plata de la que entró:
- **Concurrencia**: dos operadores de soporte (o el vendedor y soporte) refundan $80 sobre un cobro de $100 al mismo tiempo. Los dos leen "refundado: 0" y pasan la validación.
- **Sin idempotencia**: el botón "Devolver" se aprieta dos veces, o el job reintenta → dos refunds.
- **Contra lo autorizado y no lo capturado**: autorizaste $100, capturaste $80, refundás $100.
- **Refund + chargeback del mismo cobro**: el comprador abre una disputa y además soporte le devuelve la plata → la devolvés dos veces.
- **Refund de algo que nunca se cobró** (estado `FAILED` o `UNKNOWN`).

```
❌ if refundado + monto <= capturado: refundar()    (sin lock, sin key)
✅ BEGIN; SELECT ... FROM payment_orders WHERE id = ? FOR UPDATE;
   validar estado, refundado + monto <= capturado, sin disputa abierta;
   INSERT refund (idempotency_key UNIQUE); UPDATE refundado; COMMIT;
```

**Fix:** lock sobre el cobro, validar contra lo **capturado**, idempotency key por refund, y chequear disputas abiertas. Ver [implementaciones/13-refunds-y-chargebacks](../../implementaciones/13-refunds-y-chargebacks).
