# Perder (o inventar) centavos al dividir

Cada vez que se divide plata: cuotas sin interés, comisión vs vendedor, un carrito repartido entre vendedores, un descuento prorrateado entre productos, un refund parcial proporcional... Si redondeás cada parte por separado, la suma no da el total.

```
$100,00 en 3 cuotas:
❌ round(10000 / 3) × 3 = 3333 × 3 = 9999      → se perdió 1 centavo
❌ ceil(10000 / 3) × 3  = 3334 × 3 = 10002     → se inventaron 2 centavos (le cobrás de más)
✅ 3334 + 3333 + 3333   = 10000                → el resto se reparte
```

Un centavo parece nada, pero en el ledger es una transacción **desbalanceada**, y por millones de operaciones es plata real que alguien va a tener que explicar.

**Fix:** algoritmo de *allocation*: calcular las partes con división entera y repartir el resto (a las primeras, o por mayor resto, pero siempre de forma determinística). Ver [implementaciones/02-dinero-en-centavos](../../implementaciones/02-dinero-en-centavos).
