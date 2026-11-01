from decimal import Decimal, ROUND_HALF_UP

# 1000 compras de $0,10
# (ojo: sum() de Python 3.12+ compensa errores; un "total += precio" en un loop, no)
total = 0.0
for _ in range(1000):
    total += 0.1
print("❌ float:   ", total)
total_centavos = 0
for _ in range(1000):
    total_centavos += 10
print("✅ centavos:", total_centavos, "=> $" + str(total_centavos // 100) + "," + str(total_centavos % 100).zfill(2))

# comparar montos
cobrado = 0.1 + 0.2
esperado = 0.3
print("❌ ¿cobrado == esperado?", cobrado == esperado)
print("✅ ¿cobrado == esperado?", 10 + 20 == 30)

# redondeo
print("❌ round(2.675, 2) =", round(2.675, 2))
print("✅ Decimal         =", Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

# comisión del 2,9% sobre $19,99
print("❌ float:", 19.99 * 0.029)
print("✅ entero:", 1999 * 29 // 1000, "centavos (y el redondeo es una decisión explícita)")
