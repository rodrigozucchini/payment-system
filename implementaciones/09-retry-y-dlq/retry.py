import random

REINTENTABLES = {"timeout", "503", "502", "429", "connection_reset"}
TERMINALES = {"card_declined", "insufficient_funds", "invalid_card", "fraudulent"}
MAX_INTENTOS = 5

dlq = []

def espera(intento, base=1.0, tope=30.0):
    # backoff exponencial con "full jitter"
    return random.uniform(0, min(tope, base * 2 ** intento))

def ejecutar_con_retry(orden, psp):
    for intento in range(MAX_INTENTOS):
        resultado = psp(orden["id"])            # siempre la MISMA idempotency key
        if resultado == "ok":
            return "SUCCESS tras " + str(intento + 1) + " intento(s)"
        if resultado in TERMINALES:
            return "FAILED (" + resultado + "), sin reintentar"
        if resultado in REINTENTABLES:
            print("   ", resultado, "-> espero", round(espera(intento), 2), "s")
            continue
        break                                   # error que no conocemos: no adivinar
    dlq.append({"orden": orden, "ultimo_error": resultado, "intentos": intento + 1})
    return "a la DLQ"

def psp_inestable():
    respuestas = iter(["503", "timeout", "ok"])
    return lambda key: next(respuestas)

print(ejecutar_con_retry({"id": "po_1"}, psp_inestable()))
print(ejecutar_con_retry({"id": "po_2"}, lambda key: "card_declined"))
print(ejecutar_con_retry({"id": "po_3"}, lambda key: "503"))
print("DLQ:", dlq)
