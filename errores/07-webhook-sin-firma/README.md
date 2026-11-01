# Webhooks sin verificar la firma

El endpoint `/webhooks/psp` es público (el PSP tiene que poder llegar). Si no verificás que el request viene del PSP, cualquiera puede mandar `{"type": "payment.succeeded", "order": "123"}`.

Errores parecidos:
- Verificar la firma con `==` (vulnerable a *timing attacks*) en vez de comparación en tiempo constante.
- Verificar la firma sobre el JSON **re-serializado** en vez del body crudo (cambian espacios u orden de claves y la firma "falla", entonces alguien desactiva la verificación).
- No chequear el timestamp: un atacante captura un webhook real y lo **reenvía** (*replay*).
- Confiar en la IP de origen como única protección.
- Dejar el secreto del webhook en el repo.

```
❌ POST /webhooks/psp  {"status":"succeeded"}  ─► aplicar
✅ POST /webhooks/psp  Stripe-Signature: t=...,v1=...
       ─► HMAC-SHA256(secreto, t + "." + body_crudo) == v1 (compare_digest) ─► |ahora - t| < 5 min ─► aplicar
```

**Fix:** usar la función del SDK del PSP (`stripe.Webhook.construct_event`) o hacerlo como en [implementaciones/08-hosted-page-y-webhooks](../../implementaciones/08-hosted-page-y-webhooks). Y por las dudas, consultar el estado del pago a la API del PSP antes de entregar algo caro.
