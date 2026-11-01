# Webhooks duplicados y desordenados

Los PSP entregan webhooks **at-least-once** y **sin orden garantizado**: reintentan si no respondiste 2xx a tiempo, y eventos de un mismo pago pueden llegar en cualquier orden.

```
PSP emite:  processing (t1) ──► succeeded (t2)
Llega:      succeeded ──► processing ──► succeeded (reintento)

❌ status = evento.status   → termina en "processing" un rato, o te manda dos emails, o acredita dos veces
✅ dedup por event_id + solo transiciones válidas → SUCCESS, una sola vez
```

Otro clásico: procesar el webhook **adentro** del request (llamar a ledger, wallet, mandar email...) y tardar más que el timeout del PSP. El PSP lo da por fallido y lo reintenta mientras el primero sigue corriendo → procesamiento en paralelo del mismo evento.

**Fix:**
- Guardar `event_id` procesados (UNIQUE) y descartar repetidos.
- Aplicar el cambio solo si es una transición válida de la máquina de estados (un `processing` nunca pisa un `succeeded`).
- Responder 200 rápido y procesar en background desde una cola.
- Si hay dudas sobre el orden, consultar el estado actual a la API del PSP en vez de confiar en el payload.
