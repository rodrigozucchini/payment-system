# Autorización y captura (auth + capture)

Cobrar con tarjeta son en realidad **dos pasos**:

1. **Autorizar**: el emisor reserva el monto en la tarjeta del comprador (le baja el "disponible"). No se movió plata.
2. **Capturar**: el comercio confirma. Ahí entra en el próximo settlement.

Entre medio podés **anular** (*void*, gratis y sin que el comprador vea un cargo) o **capturar menos** (*partial capture*, ej. faltó un producto). Si no capturás a tiempo, la autorización **vence** (típicamente 7 días) y la reserva se libera sola.

**Ejemplo real:** hoteles y rent-a-car (reservan al hacer check-in), Uber (autoriza un estimado y captura el real), retail que captura al despachar. En Stripe: `capture_method=manual` y después `paymentIntents.capture`.

```
authorize($100) ──► AUTHORIZED ──┬── capture($80)   ──► CAPTURED (80)  ─► settlement
                                 ├── void()         ──► VOIDED         (sin cargo)
                                 └── 7 días sin nada ──► EXPIRED        (sin cargo)
```

Reglas:
- No se puede capturar más que lo autorizado (salvo tolerancias puntuales, ej. propinas).
- Capturar es idempotente: dos capturas del mismo auth no cobran dos veces.
- Si vendés algo que despachás después, autorizá al comprar y capturá al despachar: si no hay stock, hacés void en vez de refund (sin fees, sin plata ida y vuelta).
