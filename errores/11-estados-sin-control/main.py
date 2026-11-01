VALIDAS = {"NOT_STARTED": {"EXECUTING"}, "EXECUTING": {"SUCCESS", "FAILED"}}

# ❌ cualquiera setea cualquier cosa
orden = {"status": "FAILED"}
cobros = 0
def job_retries_mal(o):
    global cobros
    o["status"] = "EXECUTING"
    cobros += 1
job_retries_mal(orden)
orden["status"] = "SUCCESS"            # script de soporte
print("❌ FAILED terminó en", orden["status"], "con", cobros, "cobro(s) extra")

# ✅ todo pasa por transicionar()
def transicionar(o, desde, hacia):
    if o["status"] != desde or hacia not in VALIDAS.get(desde, set()):
        return False
    o["status"] = hacia
    return True

orden = {"status": "FAILED"}
print("✅ FAILED -> EXECUTING:", transicionar(orden, "FAILED", "EXECUTING"))
print("✅ FAILED -> SUCCESS:", transicionar(orden, "FAILED", "SUCCESS"))

# dos workers con la misma orden
orden = {"status": "EXECUTING"}
print("✅ worker A (SUCCESS):", transicionar(orden, "EXECUTING", "SUCCESS"))
print("✅ worker B (FAILED): ", transicionar(orden, "EXECUTING", "FAILED"), "-> queda", orden["status"])
