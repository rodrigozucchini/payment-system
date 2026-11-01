# No medir

Un sistema de pagos puede estar "andando" (sin errores 500, sin alertas de CPU) y estar perdiendo plata: la tasa de aprobación cayó porque un PSP rechaza más, hay 2.000 órdenes colgadas en `EXECUTING`, la DLQ creció, los webhooks dejaron de llegar hace 3 horas. Sin métricas de **negocio**, te enterás por los vendedores en redes sociales.

Qué mirar:

| Métrica | Por qué |
|---|---|
| **Tasa de aprobación** (por PSP, país, marca, emisor, BIN) | La caída es el primer síntoma de casi todo (PSP degradado, regla de fraude mal puesta, bug). |
| **Órdenes en `EXECUTING`/`UNKNOWN`/`PENDING` > X min** | Pagos colgados = plata en el limbo. |
| **Latencia p50/p99 del PSP** y tasa de timeouts | Anticipa caídas; ajustar timeouts. |
| **Webhooks recibidos por minuto** | Si baja a 0, algo se rompió (firma, endpoint, secreto rotado). |
| **Tamaño y edad de la DLQ** | Cosas que nadie está mirando. |
| **Diferencias de conciliación** (cantidad y monto) | El indicador de salud financiera. |
| **Ledger desbalanceado** | Tiene que ser siempre 0. Si no, alerta inmediata. |
| **Chargebacks / ventas** | Las redes penalizan arriba de ~1%. |
| **Refunds, payouts fallidos** | Problemas operativos y de datos de vendedores. |

Además: un **timeline por pago** (requests, respuestas del PSP, webhooks, transiciones, asientos) para que soporte responda "¿por qué falló mi pago?" sin pedirle ayuda a un developer. Y nunca loguear datos de tarjeta en ese timeline.
