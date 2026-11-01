DIAS_VENCIMIENTO = 7

def autorizar(id_pago, monto, dia):
    return {"id": id_pago, "autorizado": monto, "capturado": 0,
            "estado": "AUTHORIZED", "dia_auth": dia}

def capturar(pago, monto, dia):
    if pago["estado"] == "CAPTURED":
        return "ya capturado (idempotente): " + str(pago["capturado"])
    if pago["estado"] != "AUTHORIZED":
        return "no se puede capturar, estado " + pago["estado"]
    if dia - pago["dia_auth"] > DIAS_VENCIMIENTO:
        pago["estado"] = "EXPIRED"
        return "autorización vencida"
    if monto > pago["autorizado"]:
        return "no se puede capturar más de lo autorizado"
    pago["capturado"] = monto
    pago["estado"] = "CAPTURED"
    return "capturado " + str(monto) + " (se liberan " + str(pago["autorizado"] - monto) + ")"

def anular(pago):
    if pago["estado"] != "AUTHORIZED":
        return "no se puede anular, estado " + pago["estado"] + " (hacé un refund)"
    pago["estado"] = "VOIDED"
    return "anulado, sin cargo"

p1 = autorizar("pi_1", 10000, dia=1)
print(capturar(p1, 12000, dia=2))
print(capturar(p1, 8000, dia=2))      # faltó un producto: captura parcial
print(capturar(p1, 8000, dia=2))      # retry del job de despacho
print(anular(p1))

p2 = autorizar("pi_2", 5000, dia=1)
print(anular(p2))                      # no había stock

p3 = autorizar("pi_3", 5000, dia=1)
print(capturar(p3, 5000, dia=10))      # el despacho se demoró
