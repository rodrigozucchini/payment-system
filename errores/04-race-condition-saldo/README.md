# Race condition en el saldo (lost update)

Dos procesos leen el saldo al mismo tiempo, cada uno calcula el nuevo valor en la aplicación y lo escribe. El segundo pisa al primero.

```
saldo = 100
proceso A: lee 100 ─┐
proceso B: lee 100 ─┤  los dos ven 100 ≥ 80
proceso A: escribe 20 (paga 80)
proceso B: escribe 20 (paga 80)       → se pagaron 160 de una cuenta con 100
```

Pasa con payouts concurrentes, un refund mientras corre un payout, o el mismo evento procesado por dos workers. Los ORMs lo hacen muy fácil: `wallet.saldo -= 80; wallet.save()`.

**Fix** (cualquiera de estos):
- Update atómico con condición: `UPDATE wallets SET saldo = saldo - 80 WHERE id = ? AND saldo >= 80`.
- Lock pesimista: `SELECT ... FOR UPDATE` dentro de la transacción.
- Optimistic locking: columna `version`, `UPDATE ... WHERE version = ?`, reintentar si afectó 0 filas.
- Y como red: `CHECK (saldo >= 0)` en la tabla.

Ver [implementaciones/06-wallet-con-locking](../../implementaciones/06-wallet-con-locking).
