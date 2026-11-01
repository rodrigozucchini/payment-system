# Estados sin control

El status es una columna de texto que cualquier parte del código puede setear: `orden.status = "SUCCESS"`. Con el tiempo aparecen caminos que nadie previó:
- Un job de retries agarra una orden `FAILED` y la vuelve a `EXECUTING` → se cobra algo que el usuario ya dio por fallido (y quizás pagó con otra tarjeta).
- Un script de soporte pasa una orden `FAILED` a `SUCCESS` "porque el cliente dice que pagó" → se acredita al vendedor plata que nunca entró.
- Dos workers procesan la misma orden y cada uno escribe su resultado: gana el último.

```
❌ UPDATE payment_orders SET status = 'SUCCESS' WHERE id = 'po_1';
✅ UPDATE payment_orders SET status = 'SUCCESS' WHERE id = 'po_1' AND status = 'EXECUTING';
   + tabla de transiciones válidas en el código + historial de cambios (quién, cuándo, desde dónde)
```

**Fix:** máquina de estados explícita, toda transición pasa por una sola función, compare-and-set en la DB y una tabla de historial. Ver [implementaciones/03-maquina-de-estados](../../implementaciones/03-maquina-de-estados).
