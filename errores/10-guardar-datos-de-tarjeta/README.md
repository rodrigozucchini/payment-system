# Guardar o loguear datos de tarjeta

Nadie dice "guardemos la tarjeta en texto plano", pero se termina guardando igual:
- `logger.info(request.json())` con el body completo del checkout.
- El APM / Sentry capturando el body de un request que falló.
- Una columna `card_number` "temporal" para reintentar cobros.
- Guardar el **CVV** para no pedírselo de nuevo al usuario (**prohibido** por PCI, siempre).
- Un dump de la DB de producción en la laptop de alguien para debuggear.

Apenas un PAN toca tus sistemas (logs, DB, colas, backups), todo eso entra en **alcance PCI** y una filtración es un incidente grave (multas, perder la posibilidad de procesar tarjetas).

```
❌ log: POST /payments {"card": "4111111111111111", "cvv": "123", ...}
✅ log: POST /payments {"payment_method_token": "pm_tok_abc", "last4": "1111", ...}
```

**Fix:**
- Hosted page / campos del PSP: la tarjeta nunca pasa por tu backend.
- Guardar solo token, marca, últimos 4, vencimiento.
- Redactar/enmascarar campos sensibles en logs y en el APM (allowlist de campos que se loguean, mejor que blocklist).
- Escanear logs buscando secuencias que pasen el algoritmo de Luhn.
