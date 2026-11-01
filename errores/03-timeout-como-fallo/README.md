# Tratar un timeout como un fallo

El request al PSP salió, el PSP cobró, pero la respuesta nunca volvió (timeout, conexión cortada, el pod se reinició). Si lo marcás `FAILED`, el usuario ve "tu pago falló", vuelve a intentar... y lo cobrás dos veces. Si encima el retry usa un **id nuevo**, el PSP no puede deduplicar.

```
❌ charge(id=A) ─► PSP cobra ✓ ─✗ timeout ─► FAILED ─► usuario reintenta ─► charge(id=B) ─► PSP cobra ✓   → x2
✅ charge(id=A) ─► PSP cobra ✓ ─✗ timeout ─► UNKNOWN ─► PSP.get(A) ─► succeeded ─► SUCCESS               → x1
```

Un timeout significa **"no sé"**. Las tres respuestas posibles de una llamada remota son éxito, fallo, y desconocido.

**Fix:**
- Estado `UNKNOWN` distinto de `FAILED`.
- Consultar al PSP por el id antes de decidir; si no lo tiene, reintentar **con el mismo id**.
- Nunca generar un id nuevo para un reintento del mismo pago.
- Mostrarle al usuario "estamos procesando tu pago", no "falló".

Ver [implementaciones/10-pendientes-y-unknown](../../implementaciones/10-pendientes-y-unknown).
