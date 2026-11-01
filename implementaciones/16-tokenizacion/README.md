# Tokenización y PCI

**PCI DSS** es la norma de seguridad de las redes de tarjetas. Cuanto más contacto tenés con datos de tarjeta (PAN, CVV, banda), más pesado es cumplirla: desde un cuestionario de autoevaluación (SAQ A) hasta auditorías anuales de un QSA (nivel 1).

La forma de achicar el alcance es **no tocar nunca la tarjeta**:

```
Navegador ─► iframe/SDK del PSP ─► PSP guarda la tarjeta en su vault ─► devuelve "pm_tok_abc"
Navegador ─► nuestro backend: { payment_method_token: "pm_tok_abc" }   ← solo el token
Backend   ─► PSP: cobrar(pm_tok_abc, 5000)
```

**Ejemplo real:** Stripe Elements / `PaymentMethod`, Braintree Drop-in, Mercado Pago `cardToken`. Apple/Google Pay usan *network tokens* (el token lo emite la red, no el PSP).

Lo que podemos guardar: el token, la marca (Visa), los **últimos 4** dígitos, el vencimiento, el *fingerprint* (para detectar la misma tarjeta en dos cuentas).
Lo que **nunca** se guarda: el CVV (ni siquiera el PSP lo guarda después de autorizar). El PAN completo, solo si sos el vault y estás certificado.

Si igual tenés que tener un vault propio: cifrado con claves en un HSM/KMS, red aislada, acceso mínimo y auditado, y el resto del sistema solo ve tokens.
