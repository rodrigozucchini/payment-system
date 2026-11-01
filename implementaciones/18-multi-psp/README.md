# Routing multi-PSP y circuit breaker

Depender de un solo PSP es un punto único de falla (y de negociación). Con varios, un **router** decide a cuál mandar cada pago según:

- **Disponibilidad**: si un PSP está fallando, se lo saca de la rotación (circuit breaker).
- **Tasa de aprobación**: un PSP local suele aprobar más tarjetas locales.
- **Costo**: fees distintos por país, marca, monto.
- **Capacidades**: métodos locales (Pix, OXXO), monedas, 3DS.

**Ejemplo real:** Uber, Booking y Netflix con orquestación de pagos propia; productos como Primer, Spreedly o Gr4vy.

```
pago ─► router ─┬─► PSP A  (circuito CERRADO: anda)
                ├─► PSP B  (circuito ABIERTO: falló 5 veces, no se usa por 30s)
                └─► PSP C
```

Circuit breaker:
- **Cerrado**: todo pasa. Cuenta errores.
- **Abierto**: después de N errores seguidos, no se le manda nada por X segundos (falla rápido en vez de esperar timeouts).
- **Semi-abierto**: pasado ese tiempo, deja pasar un request de prueba; si anda, se cierra.

⚠️ **Failover solo ante errores donde seguro no se cobró** (error de conexión antes de enviar, 503 explícito). Ante un **timeout** no se puede mandar el mismo pago a otro PSP: si el primero sí cobró, le cobraste dos veces (las idempotency keys no se comparten entre PSPs). Timeout → `UNKNOWN` → consultar al PSP original.
