import hashlib
import hmac
import json

SECRETO = b"whsec_123"
pedidos = {"123": "PENDIENTE"}

def webhook_mal(body_crudo, headers):
    evento = json.loads(body_crudo)
    pedidos[evento["order"]] = "PAGADO"

def webhook_bien(body_crudo, headers):
    esperada = hmac.new(SECRETO, body_crudo.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(esperada, headers.get("X-Signature", "")):
        return 400
    evento = json.loads(body_crudo)
    pedidos[evento["order"]] = "PAGADO"
    return 200

ataque = '{"order": "123", "status": "succeeded"}'
webhook_mal(ataque, {})
print("❌ atacante sin firma:", pedidos)

pedidos["123"] = "PENDIENTE"
print("✅ atacante sin firma ->", webhook_bien(ataque, {"X-Signature": "lo_que_sea"}), pedidos)

real = '{"order": "123", "status": "succeeded"}'
firma = hmac.new(SECRETO, real.encode(), hashlib.sha256).hexdigest()   # lo hace el PSP
print("✅ PSP real ->", webhook_bien(real, {"X-Signature": firma}), pedidos)

# firmar el JSON re-serializado en vez del crudo: no coincide
reserializado = json.dumps(json.loads(real), separators=(",", ":"))
print("⚠️  body re-serializado ->", webhook_bien(reserializado, {"X-Signature": firma}), "(usá el body crudo)")
