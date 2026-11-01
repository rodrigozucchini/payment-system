# Saga con compensación

Un checkout toca varios servicios: reservar stock, cobrar, crear el envío. No hay una transacción distribuida que los cubra a todos (y 2PC entre servicios es frágil y lento). Una **saga** ejecuta los pasos en orden y, si uno falla, ejecuta las **compensaciones** de los anteriores en orden inverso.

**Ejemplo real:** checkout de un e-commerce, reservas de viaje (vuelo + hotel + auto), orquestadores como Temporal, AWS Step Functions, Camunda.

```
reservar_stock ✓ ─► autorizar_pago ✓ ─► crear_envio ✗
                                            │
liberar_stock ◄── anular_pago ◄─────────────┘   (compensaciones, en orden inverso)
```

- **Orquestada**: un coordinador (con su estado en DB) dice qué paso sigue. Más fácil de seguir y debuggear. Es lo habitual en pagos.
- **Coreografiada**: cada servicio reacciona a eventos del anterior. Menos acoplamiento, más difícil de entender.

Reglas:
- Cada paso y cada compensación son **idempotentes** (se van a reintentar).
- Las compensaciones **no pueden fallar para siempre**: se reintentan hasta que salgan, o van a una DLQ con alerta.
- Combinar con auth+capture: autorizar al principio y **capturar al final**, así la compensación es un `void` y no un refund.
- El estado de la saga se persiste en cada paso, para retomarla si se cae el orquestador.
