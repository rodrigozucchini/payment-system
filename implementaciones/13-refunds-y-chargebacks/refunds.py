import threading

cobro = {"id": "po_1", "capturado": 10000, "refundado": 0, "status": "SUCCESS"}
lock = threading.Lock()                 # SELECT ... FOR UPDATE sobre el cobro
refunds_hechos = {}                     # idempotency key -> refund
ledger = []
saldo_vendedor = {"juan": 10000}

def refund(key, monto):
    with lock:
        if key in refunds_hechos:
            return "ya existía: " + str(refunds_hechos[key])
        if cobro["status"] not in ("SUCCESS", "PARTIALLY_REFUNDED"):
            return "no se puede, estado " + cobro["status"]
        if cobro["refundado"] + monto > cobro["capturado"]:
            return "rechazado: supera lo cobrado (" + str(cobro["capturado"] - cobro["refundado"]) + " disponible)"
        cobro["refundado"] += monto
        cobro["status"] = "REFUNDED" if cobro["refundado"] == cobro["capturado"] else "PARTIALLY_REFUNDED"
        ledger.append(("refund:" + key, "vendedor:juan", "D", monto))
        ledger.append(("refund:" + key, "psp_por_cobrar", "C", monto))
        saldo_vendedor["juan"] -= monto
        refunds_hechos[key] = monto
        return "ok " + str(monto) + " -> " + cobro["status"]

print(refund("rf_a", 3000))
print(refund("rf_a", 3000))             # retry del mismo refund
print(refund("rf_b", 9000))

# dos operadores de soporte apretan "devolver $70" a la vez
resultados = []
hilos = [threading.Thread(target=lambda k=k: resultados.append(refund(k, 7000))) for k in ("rf_c", "rf_d")]
for h in hilos: h.start()
for h in hilos: h.join()
print(resultados)
print("cobro:", cobro)

# chargeback sobre otro cobro
FEE_CHARGEBACK = 1500
def chargeback(vendedor, monto):
    saldo_vendedor[vendedor] -= monto + FEE_CHARGEBACK
    ledger.append(("cb:po_9", "vendedor:" + vendedor, "D", monto + FEE_CHARGEBACK))
    ledger.append(("cb:po_9", "psp_por_cobrar", "C", monto + FEE_CHARGEBACK))

saldo_vendedor["juan"] = 0               # ya se le pagó todo en el último payout
chargeback("juan", 5000)
print("saldo juan después del chargeback:", saldo_vendedor["juan"], "(negativo: se descuenta de próximos cobros)")
