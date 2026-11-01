# Zonas horarias y cortes del día

Tu sistema guarda `created_at` en hora local de Buenos Aires (UTC-3) y sin zona. El PSP corta el día de settlement en UTC (o en la hora de Ámsterdam, o a las 18:00 de su cutoff). Resultado: los pagos entre las 21:00 y las 23:59 locales caen en "otro día" según quién mire, y **la conciliación no cierra nunca** por la misma diferencia, todos los días.

Variantes del mismo problema:
- `TIMESTAMP` sin zona: cuando el servidor cambia de región, o con horario de verano, todo se corre.
- El reporte mensual del vendedor ("lo que cobraste en noviembre") no coincide con el payout.
- Vencimientos de autorizaciones o de pagos pendientes calculados con la hora del servidor.
- Retenciones de impuestos por período fiscal local mal calculadas.

```
❌ created_at TIMESTAMP '2026-11-01 22:30'          (¿de dónde? ¿qué día es para el PSP?)
✅ created_at TIMESTAMPTZ '2026-11-02 01:30+00'     y conciliar con la ventana del PSP
```

**Fix:** guardar todo en **UTC** con zona (`TIMESTAMPTZ`), convertir a local solo para mostrar, y conciliar usando **la misma ventana de corte** que el PSP (y el `settlement_date` que trae su archivo, no tu fecha de creación).
