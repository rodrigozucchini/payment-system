import json

def luhn_valido(numero):
    # algoritmo que valida números de tarjeta: sirve para detectar PANs en logs
    total = 0
    for i, d in enumerate(reversed(numero)):
        n = int(d)
        if i % 2 == 1:
            n = n * 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

CAMPOS_LOGUEABLES = {"checkout_id", "monto", "moneda", "payment_method_token", "last4"}

def log_mal(body):
    print("❌ log:", json.dumps(body))

def log_bien(body):
    seguro = {k: v for k, v in body.items() if k in CAMPOS_LOGUEABLES}   # allowlist
    print("✅ log:", json.dumps(seguro))

def escanear_log(linea):
    for palabra in linea.replace('"', " ").replace(",", " ").split():
        if palabra.isdigit() and 13 <= len(palabra) <= 19 and luhn_valido(palabra):
            return "⚠️  posible PAN en el log: ****" + palabra[-4:]
    return "limpio"

body = {"checkout_id": "chk_1", "monto": 5000, "card": "4111111111111111", "cvv": "123"}
log_mal(body)
log_bien(body)
print(escanear_log(json.dumps(body)))
print(escanear_log('{"checkout_id": "chk_1", "pedido": 1234567890123}'))
