# No conciliar

"El código está bien testeado, la plata tiene que cuadrar." No. Hay muchísimas cosas que cambian la plata **por fuera** de tu código:
- Webhooks que nunca llegaron (o llegaron cuando tu servicio estaba caído).
- Refunds o capturas hechos a mano desde el dashboard del PSP.
- Chargebacks que el PSP descontó del settlement.
- Fees distintos a los del contrato, o que cambiaron.
- Settlements que llegan incompletos, tarde o duplicados.
- Un bug que marcó `SUCCESS` algo que el PSP rechazó.

Sin reconciliación, todo esto se acumula en silencio hasta que el contador te dice que faltan $40.000 y nadie sabe desde cuándo.

```
❌ nuestro sistema: $1.000.000 cobrados  |  banco: $987.340  →  ¿y la diferencia? nadie mira
✅ cada día: payment_orders ⇄ settlement PSP ⇄ extracto del banco ⇄ ledger ⇄ wallet
   → diferencias clasificadas, montos, alerta si > umbral, dashboard para finanzas
```

**Fix:** reconciliación diaria automática en los tres niveles (interno, contra PSP, contra banco), con clasificación de diferencias y alertas. Ver [implementaciones/12-reconciliacion](../../implementaciones/12-reconciliacion).
