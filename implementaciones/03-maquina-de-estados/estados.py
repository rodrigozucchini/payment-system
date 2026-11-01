TRANSICIONES = {
    "NOT_STARTED":        ["EXECUTING"],
    "EXECUTING":          ["SUCCESS", "FAILED", "PENDING", "UNKNOWN"],
    "PENDING":            ["SUCCESS", "FAILED"],
    "UNKNOWN":            ["SUCCESS", "FAILED", "EXECUTING"],   # EXECUTING: re-ejecutar con la MISMA key
    "SUCCESS":            ["PARTIALLY_REFUNDED", "REFUNDED", "CHARGEBACK"],
    "PARTIALLY_REFUNDED": ["PARTIALLY_REFUNDED", "REFUNDED", "CHARGEBACK"],
    "FAILED":             [],
    "REFUNDED":           [],
    "CHARGEBACK":         [],
}

class TransicionInvalida(Exception):
    pass

def transicionar(orden, desde, hacia):
    # equivale a: UPDATE ... SET status = hacia WHERE id = ? AND status = desde
    if orden["status"] != desde:
        return False                     # alguien la movió antes: 0 filas afectadas
    if hacia not in TRANSICIONES[desde]:
        raise TransicionInvalida(desde + " -> " + hacia)
    orden["status"] = hacia
    orden["historial"].append(desde + " -> " + hacia)   # auditoría
    return True

orden = {"id": "po_1", "status": "NOT_STARTED", "historial": []}

transicionar(orden, "NOT_STARTED", "EXECUTING")
transicionar(orden, "EXECUTING", "SUCCESS")
print("estado:", orden["status"])

# un webhook viejo que dice "processing" llega tarde
print("webhook viejo aplicado?", transicionar(orden, "EXECUTING", "PENDING"))

try:
    transicionar(orden, "SUCCESS", "FAILED")
except TransicionInvalida as e:
    print("bloqueado:", e)

transicionar(orden, "SUCCESS", "REFUNDED")
print("historial:", orden["historial"])
