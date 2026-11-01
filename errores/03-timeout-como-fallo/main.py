import uuid

cobros_psp = {}

def psp_charge(key, monto, perder_respuesta):
    if key not in cobros_psp:
        cobros_psp[key] = monto          # el PSP cobró
    if perder_respuesta:
        raise TimeoutError()             # pero no nos enteramos
    return "succeeded"

def psp_get(key):
    return "succeeded" if key in cobros_psp else "not_found"

def pagar_mal(monto, perder_respuesta):
    key = str(uuid.uuid4())              # id nuevo en cada intento
    try:
        psp_charge(key, monto, perder_respuesta)
        return "SUCCESS"
    except TimeoutError:
        return "FAILED"

def pagar_bien(payment_order_id, monto, perder_respuesta):
    try:
        psp_charge(payment_order_id, monto, perder_respuesta)
        return "SUCCESS"
    except TimeoutError:
        return "UNKNOWN"

# ❌
estado = pagar_mal(5000, perder_respuesta=True)
print("❌ estado:", estado, "-> el usuario reintenta")
pagar_mal(5000, perder_respuesta=False)
print("❌ cobrado en el PSP:", sum(cobros_psp.values()))

# ✅
cobros_psp.clear()
estado = pagar_bien("po_1", 5000, perder_respuesta=True)
print("✅ estado:", estado, "-> consulto al PSP:", psp_get("po_1"))
if psp_get("po_1") == "not_found":
    pagar_bien("po_1", 5000, perder_respuesta=False)
print("✅ cobrado en el PSP:", sum(cobros_psp.values()))
