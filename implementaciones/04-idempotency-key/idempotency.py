import hashlib
import json

claves = {}     # tabla idempotency_keys: key -> {hash, estado, respuesta}
cobros = []

class UniqueViolation(Exception):
    pass

def insert_unique(key, fila):
    # en la DB real esto es un INSERT con UNIQUE constraint: atómico
    if key in claves:
        raise UniqueViolation()
    claves[key] = fila

def hash_body(body):
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()

def post_payments(idempotency_key, body):
    h = hash_body(body)
    try:
        insert_unique(idempotency_key, {"hash": h, "estado": "EN_CURSO", "respuesta": None})
    except UniqueViolation:
        fila = claves[idempotency_key]
        if fila["hash"] != h:
            return 422, {"error": "Idempotency-Key reutilizada con otro body"}
        if fila["estado"] == "EN_CURSO":
            return 409, {"error": "en curso, reintentá", "retry_after": 1}
        return fila["respuesta"]           # misma respuesta que la primera vez

    cobros.append(body["monto"])           # acá iría el cobro real
    respuesta = (200, {"status": "SUCCESS", "monto": body["monto"]})
    claves[idempotency_key]["estado"] = "TERMINADO"
    claves[idempotency_key]["respuesta"] = respuesta
    return respuesta

body = {"checkout_id": "chk_1", "monto": 5000}
print(post_payments("key-abc", body))
print(post_payments("key-abc", body))                          # doble click
print(post_payments("key-abc", {"checkout_id": "chk_1", "monto": 9999}))
claves["key-xyz"] = {"hash": hash_body(body), "estado": "EN_CURSO", "respuesta": None}
print(post_payments("key-xyz", body))                          # simultáneo con uno en curso
print("cobros realizados:", cobros)                            # [5000] -> uno solo
