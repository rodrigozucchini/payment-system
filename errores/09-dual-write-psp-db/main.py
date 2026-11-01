psp = {}

def psp_charge(key, monto):
    psp[key] = monto

def pagar_mal(db, key, monto, crash):
    psp_charge(key, monto)
    if crash:
        return                       # 💥 se cae el proceso
    db[key] = "SUCCESS"

def pagar_bien(db, key, monto, crash):
    db[key] = "EXECUTING"            # intención persistida ANTES
    psp_charge(key, monto)
    if crash:
        return                       # 💥
    db[key] = "SUCCESS"

def barredora(db):
    for key, estado in db.items():
        if estado == "EXECUTING" and key in psp:
            db[key] = "SUCCESS"

db = {}
pagar_mal(db, "po_1", 5000, crash=True)
barredora(db)
print("❌ PSP:", psp, "| nuestra DB:", db, "-> plata cobrada sin registro")

psp.clear()
db = {}
pagar_bien(db, "po_1", 5000, crash=True)
print("✅ después del crash:", db)
barredora(db)
print("✅ después de la barredora:", db)
