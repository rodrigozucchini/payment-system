# Hosted payment page + webhooks firmados

Para no tocar nunca la tarjeta (y no cargar con PCI completo), el usuario la carga en una página o iframe **del PSP**. Nosotros registramos el pago, recibimos un token/URL, redirigimos, y después el PSP nos avisa el resultado por **webhook**.

**Ejemplo real:** Stripe Checkout / Payment Element, Mercado Pago Checkout Pro, Adyen Drop-in, PayPal.

```
1. Navegador ─► nosotros: POST /checkout
2. nosotros  ─► PSP: registrar pago (monto, moneda, idempotency=payment_order_id, redirect_url)
3. PSP       ─► nosotros: token / session_url        (lo guardamos en la DB)
4. Navegador ─► página del PSP: carga la tarjeta, 3DS, etc.
5. PSP       ─► Navegador: redirect a /success?session=...   ← solo para mostrar algo, NO es la verdad
6. PSP       ─► nosotros: POST /webhooks/psp (firmado)        ← ESTA es la verdad (o consultar la API)
```

El webhook hay que:
- **Verificar la firma** (HMAC-SHA256 del body con un secreto compartido), comparando en **tiempo constante** (`hmac.compare_digest`).
- **Rechazar timestamps viejos** (ej. > 5 min) para evitar *replay attacks*.
- **Deduplicar por `event_id`**: el PSP reintenta si no le respondemos 2xx rápido.
- **Aplicar solo transiciones válidas**: los webhooks pueden llegar desordenados.
- **Responder 200 rápido** y procesar en background (encolar), si no el PSP lo da por fallido y reintenta.
- Opcional pero recomendado: ante un webhook, **consultar la API del PSP** por el estado real del pago.
