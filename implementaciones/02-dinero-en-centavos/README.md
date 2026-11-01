# Dinero en centavos (minor units) y repartos

La plata se guarda como **entero en la unidad mínima** de la moneda, junto con la moneda. `1050 USD` = $10,50. Así no hay errores de redondeo binario y las sumas son exactas.

**Ejemplo real:** Stripe (`amount: 1050`), Adyen (`value: 1050, currency: "EUR"`), columnas `BIGINT` en el ledger.

```
"10.50" (string del cliente) ─► Decimal("10.50") ─► × 10^exponente ─► 1050 (int)
                                                     USD: 2, JPY: 0, KWD: 3
```

Cuando hay que **dividir** (comisiones, cuotas, split entre vendedores) no alcanza con redondear cada parte: se reparte el resto para que la suma dé exacta.

```
$100,00 en 3 ─► 10000 // 3 = 3333, resto 1 ─► [3334, 3333, 3333]   suma = 10000 ✅
```

Reglas:
- Nunca `float`. En la entrada usá `Decimal` desde un **string**; adentro, enteros.
- La moneda viaja **siempre** con el monto. No se suman monedas distintas.
- Redondeo explícito y documentado (`ROUND_HALF_EVEN`, "bancario", o lo que pida el negocio/regulación).
