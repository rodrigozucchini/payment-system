import hashlib
import hmac
import json
import time

SECRETO = b"whsec_compartido_con_el_psp"
TOLERANCIA_SEG = 300

pagos = {"po_1": {"status": "EXECUTING"}}
eventos_procesados = set()
VALIDAS = {"EXECUTING": ["PENDING", "SUCCESS", "FAILED"], "PENDING": ["SUCCESS", "FAILED"]}

# --- lo que hace el PSP ---
def psp_firmar(body, ts):
    firmado = (str(ts) + "." + body).encode()
    return hmac.new(SECRETO, firmado, hashlib.sha256).hexdigest()

# --- nuestro endpoint ---
def recibir_webhook(body, header_ts, header_firma, ahora):
    esperada = psp_firmar(body, header_ts)
    if not hmac.compare_digest(esperada, header_firma):
        return 400, "firma inválida"
    if abs(ahora - header_ts) > TOLERANCIA_SEG:
        return 400, "timestamp viejo (replay?)"

    evento = json.loads(body)
    if evento["event_id"] in eventos_procesados:
        return 200, "duplicado, ignorado"

    pago = pagos[evento["payment_order_id"]]
    nuevo = evento["status"]
    if nuevo in VALIDAS.get(pago["status"], []):
        pago["status"] = nuevo
        resultado = "aplicado -> " + nuevo
    else:
        resultado = "ignorado (" + pago["status"] + " -> " + nuevo + " no es válida)"
    eventos_procesados.add(evento["event_id"])
    return 200, resultado

ahora = int(time.time())
ok = json.dumps({"event_id": "evt_2", "payment_order_id": "po_1", "status": "SUCCESS"})
viejo = json.dumps({"event_id": "evt_1", "payment_order_id": "po_1", "status": "PENDING"})

print(recibir_webhook(ok, ahora, psp_firmar(ok, ahora), ahora))
print(recibir_webhook(ok, ahora, psp_firmar(ok, ahora), ahora))         # reintento del PSP
print(recibir_webhook(viejo, ahora, psp_firmar(viejo, ahora), ahora))   # llegó desordenado
falso = json.dumps({"event_id": "evt_x", "payment_order_id": "po_1", "status": "SUCCESS"})
print(recibir_webhook(falso, ahora, "firma_inventada", ahora))          # atacante
print(recibir_webhook(ok, ahora - 3600, psp_firmar(ok, ahora - 3600), ahora))  # replay de hace 1 h
print("estado final:", pagos["po_1"])
