# Usar float para la plata

Los `float`/`double` son binarios: no pueden representar exacto `0.1`. Cada operación agrega un error chiquito que, sumado en miles de transacciones, hace que el ledger no cierre, que una comparación `==` falle o que se cobre un centavo de más.

```
❌ 0.1 + 0.2            = 0.30000000000000004
❌ total += 0.1 (×1000) = 99.9999999999986
❌ round(2.675, 2)     = 2.67   (esperabas 2.68)
✅ 10 + 20             = 30     (centavos, enteros)
✅ Decimal("0.1") + Decimal("0.2") = Decimal("0.3")
```

Pasa también en JSON: `{"amount": 10.50}` lo parsea como float casi cualquier lenguaje. Y en JavaScript **todos** los números son float.

**Fix:** enteros en unidad mínima (`BIGINT amount_minor`) + moneda. En la API, string o entero. Si hace falta decimales (tasas, prorrateos), `Decimal` con redondeo explícito, y convertir a entero al final. Ver [implementaciones/02-dinero-en-centavos](../../implementaciones/02-dinero-en-centavos).
