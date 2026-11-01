TERMINALES = {"card_declined", "insufficient_funds", "expired_card", "fraudulent"}

def emisor():
    # el emisor rechaza; después de 3 rechazos seguidos bloquea la tarjeta por sospecha
    estado = {"intentos": 0}
    def charge():
        estado["intentos"] += 1
        if estado["intentos"] > 3:
            return "card_blocked"
        return "insufficient_funds"
    return charge, estado

charge, estado = emisor()
for _ in range(5):
    r = charge()
print("❌ reintentar todo:", estado["intentos"], "intentos, último resultado:", r, "(le bloqueaste la tarjeta)")

charge, estado = emisor()
for _ in range(5):
    r = charge()
    if r in TERMINALES:
        break
print("✅ clasificar errores:", estado["intentos"], "intento, resultado:", r, "-> avisar al usuario que use otro medio")

# retries en capas
SDK, CODIGO, COLA = 3, 3, 3
print("❌ retries en 3 capas:", SDK * CODIGO * COLA, "llamadas al PSP por un solo pago")
