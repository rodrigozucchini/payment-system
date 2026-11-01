from decimal import Decimal, ROUND_HALF_EVEN

EXPONENTE = {"USD": 2, "ARS": 2, "EUR": 2, "JPY": 0, "KWD": 3}

def a_minor(monto_str, moneda):
    # "10.50" -> 1050. Siempre desde string, nunca desde float.
    factor = Decimal(10) ** EXPONENTE[moneda]
    valor = (Decimal(monto_str) * factor).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)
    return int(valor)

def a_texto(minor, moneda):
    exp = EXPONENTE[moneda]
    valor = Decimal(minor).scaleb(-exp)     # 1050 -> 10.50
    return str(valor) + " " + moneda

def repartir(total, n):
    # divide total (entero) en n partes que suman exactamente total
    base = total // n
    resto = total % n
    return [base + 1 if i < resto else base for i in range(n)]

def repartir_por_peso(total, pesos):
    # ej: comisión 3% / vendedor 97%, o split entre vendedores por monto
    suma_pesos = sum(pesos)
    partes = [total * p // suma_pesos for p in pesos]
    faltante = total - sum(partes)
    for i in range(faltante):
        partes[i] += 1
    return partes

print(a_minor("10.50", "USD"), a_minor("1500", "JPY"), a_minor("1.234", "KWD"))
print(a_texto(1050, "USD"))

print("3 cuotas de $100:", repartir(10000, 3), "suma:", sum(repartir(10000, 3)))
print("split 97/3 de $10,01:", repartir_por_peso(1001, [97, 3]))
print("float:", 0.1 + 0.2, "| centavos:", 10 + 20)
