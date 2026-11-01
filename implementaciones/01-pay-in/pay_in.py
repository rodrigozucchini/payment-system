# "Tablas"
payment_events = {}
payment_orders = {}
wallet = {}          # saldo por vendedor, en centavos
ledger = []          # asientos

COMISION_PORCIENTO = 3   # 3% para la plataforma (entero, nada de floats)

# --- PSP falso ---
cobros_psp = {}      # el PSP también deduplica por idempotency key

def psp_charge(idempotency_key, monto, token_tarjeta):
    if idempotency_key in cobros_psp:
        return cobros_psp[idempotency_key]       # ya lo cobré, devuelvo lo mismo
    if token_tarjeta == "tok_rechazada":
        resultado = {"status": "failed", "reason": "card_declined"}
    else:
        resultado = {"status": "succeeded", "psp_id": "ch_" + idempotency_key}
    cobros_psp[idempotency_key] = resultado
    return resultado

# --- Wallet y Ledger ---
def actualizar_wallet(orden):
    comision = orden["monto"] * COMISION_PORCIENTO // 100
    vendedor = orden["vendedor"]
    wallet[vendedor] = wallet.get(vendedor, 0) + orden["monto"] - comision
    orden["wallet_updated"] = True

def actualizar_ledger(orden):
    comision = orden["monto"] * COMISION_PORCIENTO // 100
    tx = orden["id"]
    ledger.append({"tx": tx, "cuenta": "psp_por_cobrar", "debito": orden["monto"], "credito": 0})
    ledger.append({"tx": tx, "cuenta": "vendedor:" + orden["vendedor"], "debito": 0, "credito": orden["monto"] - comision})
    ledger.append({"tx": tx, "cuenta": "ingresos:comision", "debito": 0, "credito": comision})
    orden["ledger_updated"] = True

# --- Executor ---
def ejecutar_orden(orden, token_tarjeta):
    orden["status"] = "EXECUTING"              # se guarda ANTES de llamar al PSP
    respuesta = psp_charge(orden["id"], orden["monto"], token_tarjeta)
    if respuesta["status"] == "succeeded":
        orden["status"] = "SUCCESS"
        orden["psp_id"] = respuesta["psp_id"]
        actualizar_wallet(orden)
        actualizar_ledger(orden)
    else:
        orden["status"] = "FAILED"
        orden["motivo"] = respuesta["reason"]

# --- Payment Service ---
def crear_pago(checkout_id, token_tarjeta, ordenes):
    payment_events[checkout_id] = {"checkout_id": checkout_id, "done": False}
    for o in ordenes:
        payment_orders[o["id"]] = {
            "id": o["id"], "checkout_id": checkout_id, "vendedor": o["vendedor"],
            "monto": o["monto"], "status": "NOT_STARTED",
            "ledger_updated": False, "wallet_updated": False,
        }
    for o in ordenes:
        ejecutar_orden(payment_orders[o["id"]], token_tarjeta)
    payment_events[checkout_id]["done"] = True

crear_pago("chk_1", "tok_visa", [
    {"id": "po_1", "vendedor": "juan", "monto": 10000},   # $100,00
    {"id": "po_2", "vendedor": "ana",  "monto": 2550},    # $25,50
])
crear_pago("chk_2", "tok_rechazada", [{"id": "po_3", "vendedor": "juan", "monto": 5000}])

for o in payment_orders.values():
    print(o["id"], o["status"], "ledger:", o["ledger_updated"], "wallet:", o["wallet_updated"])
print("wallet:", wallet)       # juan 9700, ana 2474

debitos = sum(a["debito"] for a in ledger)
creditos = sum(a["credito"] for a in ledger)
print("ledger cierra:", debitos == creditos, debitos, creditos)
