import math

def repartir_mal(total, n):
    return [round(total / n)] * n

def repartir_ceil(total, n):
    return [math.ceil(total / n)] * n

def repartir_bien(total, n):
    base, resto = divmod(total, n)
    return [base + 1 if i < resto else base for i in range(n)]

total = 10000
for f, s in ((repartir_mal, "❌"), (repartir_ceil, "❌"), (repartir_bien, "✅")):
    partes = f(total, 3)
    print(s, f.__name__, partes, "suma:", sum(partes), "diferencia:", sum(partes) - total)

# split de un carrito de $10,00 con descuento de $1,00 prorrateado entre 3 productos de $3,33/$3,33/$3,34
precios = [333, 333, 334]
descuento = 100
mal = [round(descuento * p / sum(precios)) for p in precios]
print("❌ descuento prorrateado:", mal, "suma:", sum(mal))

partes = [descuento * p // sum(precios) for p in precios]
for i in range(descuento - sum(partes)):
    partes[i] += 1
print("✅ descuento prorrateado:", partes, "suma:", sum(partes))
