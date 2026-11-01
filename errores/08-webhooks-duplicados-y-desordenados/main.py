llegadas = [
    {"event_id": "evt_2", "status": "succeeded"},
    {"event_id": "evt_1", "status": "processing"},     # viejo, llegó tarde
    {"event_id": "evt_2", "status": "succeeded"},      # reintento del PSP
]

# ❌
pago = {"status": "EXECUTING"}
saldo = 0
for e in llegadas:
    pago["status"] = e["status"]
    if e["status"] == "succeeded":
        saldo += 5000
print("❌ estado:", pago["status"], "| saldo acreditado:", saldo)

# ✅
MAPA = {"processing": "PENDING", "succeeded": "SUCCESS", "failed": "FAILED"}
VALIDAS = {"EXECUTING": {"PENDING", "SUCCESS", "FAILED"}, "PENDING": {"SUCCESS", "FAILED"}}
pago = {"status": "EXECUTING"}
saldo = 0
vistos = set()
for e in llegadas:
    if e["event_id"] in vistos:
        continue
    vistos.add(e["event_id"])
    nuevo = MAPA[e["status"]]
    if nuevo not in VALIDAS.get(pago["status"], set()):
        continue
    pago["status"] = nuevo
    if nuevo == "SUCCESS":
        saldo += 5000
print("✅ estado:", pago["status"], "| saldo acreditado:", saldo)
