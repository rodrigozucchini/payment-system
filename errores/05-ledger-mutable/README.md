# Ledger mutable

Alguien carga mal un asiento y lo "arregla" con un `UPDATE`. O se borra un cobro duplicado con `DELETE`. Los saldos quedan bien, pero:
- Se perdió **qué pasó y cuándo**. Un auditor (o un juez) no puede reconstruir la historia.
- Los reportes que ya se generaron (impuestos, payouts) dejan de coincidir con el ledger.
- No hay forma de detectar si alguien está manipulando montos.

```
❌ UPDATE ledger SET amount = 9000 WHERE id = 42;     (antes era 10000: ¿quién? ¿por qué?)
✅ INSERT asiento de reversa  (-10000)  tx: "correccion:42", motivo: "monto mal cargado", autor: "ops:maria"
   INSERT asiento correcto    (+9000)
```

**Fix:**
- Ledger **append-only**: sin permisos de `UPDATE`/`DELETE` para el usuario de la aplicación (`REVOKE UPDATE, DELETE ON ledger_entries`).
- Correcciones con asientos de reversa que referencian al original, con motivo y autor.
- Opcional: encadenar hashes de los asientos (cada uno incluye el hash del anterior) para detectar manipulación.
