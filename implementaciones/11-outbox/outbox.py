ordenes = {"po_1": {"status": "EXECUTING", "monto": 10000, "vendedor": "juan",
                    "ledger_updated": False, "wallet_updated": False}}
outbox = []
broker = {"ledger": [], "wallet": []}   # pub/sub: cada suscriptor tiene su cola

def marcar_exitoso(id_orden):
    # BEGIN
    ordenes[id_orden]["status"] = "SUCCESS"
    outbox.append({"evento": "pago.exitoso", "id": id_orden, "enviado": False})
    # COMMIT -> se guardan los dos o ninguno

def relay(caerse_antes_de_marcar=False):
    for fila in outbox:
        if fila["enviado"]:
            continue
        for cola in broker.values():
            cola.append(fila["id"])
        if caerse_antes_de_marcar:
            return                       # publicó pero no llegó a marcar: se va a publicar de nuevo
        fila["enviado"] = True

asientos = []
procesados_ledger = set()
saldos = {}
procesados_wallet = set()

def consumidor_ledger():
    while broker["ledger"]:
        id_orden = broker["ledger"].pop(0)
        if id_orden in procesados_ledger:
            continue
        o = ordenes[id_orden]
        asientos.append(("psp_por_cobrar", "D", o["monto"]))
        asientos.append(("vendedor:" + o["vendedor"], "C", o["monto"]))
        procesados_ledger.add(id_orden)     # en la misma tx que los asientos
        o["ledger_updated"] = True

def consumidor_wallet():
    while broker["wallet"]:
        id_orden = broker["wallet"].pop(0)
        if id_orden in procesados_wallet:
            continue
        o = ordenes[id_orden]
        saldos[o["vendedor"]] = saldos.get(o["vendedor"], 0) + o["monto"]
        procesados_wallet.add(id_orden)
        o["wallet_updated"] = True

marcar_exitoso("po_1")
relay(caerse_antes_de_marcar=True)
relay()                                  # vuelve el relay: publica otra vez
print("mensajes en el broker:", broker)
consumidor_ledger()
consumidor_wallet()
print("asientos:", asientos)
print("saldos:", saldos)                 # 10000, no 20000
print("orden:", ordenes["po_1"])
