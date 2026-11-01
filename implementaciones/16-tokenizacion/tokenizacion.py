import hashlib
import secrets

# ---- esto vive en el PSP (o en un vault aislado y certificado) ----
_vault = {}

def vault_tokenizar(pan, vencimiento, cvv):
    # el CVV se usa para la primera autorización y se descarta: nunca se guarda
    token = "pm_tok_" + secrets.token_hex(8)
    _vault[token] = {"pan": pan, "vencimiento": vencimiento}
    return {
        "token": token,
        "marca": "visa" if pan.startswith("4") else "otra",
        "ultimos4": pan[-4:],
        "vencimiento": vencimiento,
        "fingerprint": hashlib.sha256(("sal_del_psp" + pan).encode()).hexdigest()[:16],
    }

def vault_cobrar(token, monto):
    return "cobrado " + str(monto) + " a tarjeta ****" + _vault[token]["pan"][-4:]

# ---- esto es nuestro sistema: nunca ve el PAN ----
metodos_de_pago = {}

def guardar_metodo(usuario, datos_del_psp):
    metodos_de_pago[usuario] = datos_del_psp

def mascarar(texto):
    # por si algo se cuela en un log: dejar solo los últimos 4 de cualquier secuencia de 13-19 dígitos
    resultado, digitos = "", ""
    for ch in texto + " ":
        if ch.isdigit():
            digitos += ch
            continue
        if 13 <= len(digitos) <= 19:
            digitos = "*" * (len(digitos) - 4) + digitos[-4:]
        resultado += digitos + ch
        digitos = ""
    return resultado[:-1]

datos = vault_tokenizar("4111111111111111", "12/29", "123")   # pasa en el iframe del PSP
guardar_metodo("usr_9", datos)
print("lo que guardamos:", metodos_de_pago["usr_9"])
print(vault_cobrar(metodos_de_pago["usr_9"]["token"], 5000))
print("log:", mascarar("request body: card=4111111111111111 monto=5000"))
