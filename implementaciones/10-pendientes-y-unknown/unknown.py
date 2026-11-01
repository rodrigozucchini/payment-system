# El PSP sí cobró po_1, pero la respuesta se perdió en la red
psp_db = {}

def psp_charge(key, monto, cortar_respuesta=False):
    if key not in psp_db:
        psp_db[key] = {"status": "succeeded", "monto": monto}
    if cortar_respuesta:
        raise TimeoutError()
    return psp_db[key]

def psp_get(key):
    return psp_db.get(key, {"status": "not_found"})

ordenes = {
    "po_1": {"monto": 5000, "status": "NOT_STARTED"},
    "po_2": {"monto": 3000, "status": "NOT_STARTED"},
}

def ejecutar(id_orden, cortar_respuesta=False):
    o = ordenes[id_orden]
    o["status"] = "EXECUTING"
    try:
        r = psp_charge(id_orden, o["monto"], cortar_respuesta)
        o["status"] = "SUCCESS" if r["status"] == "succeeded" else "FAILED"
    except TimeoutError:
        o["status"] = "UNKNOWN"          # NO "FAILED"

def barredora():
    for id_orden, o in ordenes.items():
        if o["status"] not in ("UNKNOWN", "EXECUTING", "PENDING"):
            continue
        r = psp_get(id_orden)
        if r["status"] == "succeeded":
            o["status"] = "SUCCESS"
        elif r["status"] == "failed":
            o["status"] = "FAILED"
        elif r["status"] == "not_found":
            ejecutar(id_orden)           # misma key: si el original llega tarde, el PSP deduplica
        print("barredora:", id_orden, "->", o["status"])

ejecutar("po_1", cortar_respuesta=True)
ordenes["po_2"]["status"] = "UNKNOWN"    # se cayó la conexión antes de llegar al PSP
print("antes:", {k: v["status"] for k, v in ordenes.items()})
barredora()
print("cobros en el PSP:", psp_db)       # uno por orden, ninguno doble
