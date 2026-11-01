intentos_por_tarjeta = {}     # en la vida real: Redis con TTL (ventana deslizante)
BLOQUEADAS = {"fp_robada"}

def score(pago, minuto):
    puntos = 0
    motivos = []
    ventana = [m for m in intentos_por_tarjeta.get(pago["fingerprint"], []) if minuto - m < 10]
    ventana.append(minuto)
    intentos_por_tarjeta[pago["fingerprint"]] = ventana
    if len(ventana) > 3:
        puntos += 70; motivos.append("velocity: " + str(len(ventana)) + " intentos en 10 min")
    if pago["pais_ip"] != pago["pais_tarjeta"]:
        puntos += 25; motivos.append("país IP != país tarjeta")
    if pago["cuenta_dias"] < 1 and pago["monto"] > 50000:
        puntos += 30; motivos.append("cuenta nueva + monto alto")
    if pago["fingerprint"] in BLOQUEADAS:
        puntos += 100; motivos.append("tarjeta bloqueada")
    return puntos, motivos

def decidir(pago, minuto):
    puntos, motivos = score(pago, minuto)
    if puntos >= 70:
        decision = "RECHAZAR"
    elif puntos >= 25:
        decision = "PEDIR_3DS"
    else:
        decision = "APROBAR"
    return decision, puntos, motivos

normal = {"fingerprint": "fp_1", "pais_ip": "AR", "pais_tarjeta": "AR", "cuenta_dias": 400, "monto": 5000}
viajero = {"fingerprint": "fp_2", "pais_ip": "ES", "pais_tarjeta": "AR", "cuenta_dias": 400, "monto": 5000}
nuevo = {"fingerprint": "fp_3", "pais_ip": "US", "pais_tarjeta": "AR", "cuenta_dias": 0, "monto": 90000}

print(decidir(normal, 0))
print(decidir(viajero, 0))
print(decidir(nuevo, 0))
print("card testing:")
for m in range(5):
    print("  ", decidir({"fingerprint": "fp_4", "pais_ip": "AR", "pais_tarjeta": "AR",
                         "cuenta_dias": 30, "monto": 100}, m))
