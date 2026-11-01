# Riesgo y fraude

Antes de mandar un cobro al PSP se evalúa el riesgo. Fraude aprobado = chargeback (perdés la plata + el producto + fee). Fraude rechazado de más = ventas perdidas. Es un balance.

**Ejemplo real:** Stripe Radar, Adyen RevenueProtect, Sift, Signifyd, Riskified; modelos propios en Mercado Libre o Amazon.

```
pago ─► reglas + score ─┬─ score bajo    ─► aprobar
                        ├─ score medio   ─► pedir 3DS / revisión manual (PENDING)
                        └─ score alto    ─► rechazar
```

Señales típicas:
- **Velocity**: muchos intentos de la misma tarjeta / IP / dispositivo / email en poco tiempo (*card testing*: probar tarjetas robadas con montos chicos).
- **Inconsistencias**: país de la IP ≠ país de la tarjeta ≠ dirección de envío.
- **Historial**: cuenta nueva, primer compra, monto muy por encima del habitual.
- **Listas**: tarjetas/emails/dispositivos bloqueados, listas de sanciones (OFAC) y AML para montos grandes o payouts.
- **AVS / CVV**: el banco confirma si la dirección y el código coinciden.

**3DS** es la herramienta clave: el banco autentica al comprador y, si después hay un chargeback por fraude, la responsabilidad pasa al emisor (*liability shift*). En Europa es obligatorio (SCA/PSD2).
