import hashlib

def saldo(ledger, cuenta):
    return sum(a["monto"] for a in ledger if a["cuenta"] == cuenta)

# ❌ corregir editando
ledger_mal = [{"id": 1, "cuenta": "juan", "monto": 10000}]
ledger_mal[0]["monto"] = 9000
print("❌ saldo:", saldo(ledger_mal, "juan"), "| historia:", ledger_mal, "-> ¿qué pasó?")

# ✅ corregir con reversa, encadenando hashes
ledger = []
def agregar(cuenta, monto, motivo):
    anterior = ledger[-1]["hash"] if ledger else "genesis"
    contenido = anterior + cuenta + str(monto) + motivo
    ledger.append({"id": len(ledger) + 1, "cuenta": cuenta, "monto": monto,
                   "motivo": motivo, "hash": hashlib.sha256(contenido.encode()).hexdigest()[:12]})

def verificar():
    anterior = "genesis"
    for a in ledger:
        contenido = anterior + a["cuenta"] + str(a["monto"]) + a["motivo"]
        if hashlib.sha256(contenido.encode()).hexdigest()[:12] != a["hash"]:
            return "manipulado en el asiento " + str(a["id"])
        anterior = a["hash"]
    return "íntegro"

agregar("juan", 10000, "cobro po_1")
agregar("juan", -10000, "reversa de #1: monto mal cargado (ops:maria)")
agregar("juan", 9000, "cobro po_1 corregido")
print("✅ saldo:", saldo(ledger, "juan"))
for a in ledger: print("   ", a)
print("✅ verificación:", verificar())

ledger[0]["monto"] = 50000          # alguien edita a escondidas
print("✅ verificación:", verificar())
