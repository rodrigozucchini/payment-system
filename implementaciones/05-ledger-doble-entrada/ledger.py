asientos = []
transacciones_ids = set()

TIPO_CUENTA = {
    "psp_por_cobrar": "activo",
    "banco": "activo",
    "vendedor:juan": "pasivo",       # plata que le debemos a Juan
    "ingresos:comision": "ingreso",
    "gastos:fee_psp": "gasto",
}

class TransaccionDesbalanceada(Exception):
    pass

def registrar(tx_id, patas):
    # patas: lista de (cuenta, "D" o "C", monto en centavos)
    if tx_id in transacciones_ids:
        return False                                 # idempotente
    debe = sum(m for c, lado, m in patas if lado == "D")
    haber = sum(m for c, lado, m in patas if lado == "C")
    if debe != haber or debe == 0:
        raise TransaccionDesbalanceada(tx_id + ": " + str(debe) + " != " + str(haber))
    # BEGIN; INSERT de todas las patas; COMMIT
    for cuenta, lado, monto in patas:
        asientos.append({"tx": tx_id, "cuenta": cuenta, "lado": lado, "monto": monto})
    transacciones_ids.add(tx_id)
    return True

def saldo(cuenta):
    d = sum(a["monto"] for a in asientos if a["cuenta"] == cuenta and a["lado"] == "D")
    c = sum(a["monto"] for a in asientos if a["cuenta"] == cuenta and a["lado"] == "C")
    if TIPO_CUENTA[cuenta] in ("activo", "gasto"):
        return d - c
    return c - d

# cobro de $100 con 3% de comisión
registrar("cobro:po_1", [("psp_por_cobrar", "D", 10000),
                         ("vendedor:juan", "C", 9700),
                         ("ingresos:comision", "C", 300)])
registrar("cobro:po_1", [("psp_por_cobrar", "D", 10000),        # el evento llegó dos veces
                         ("vendedor:juan", "C", 9700),
                         ("ingresos:comision", "C", 300)])
# el PSP liquida: entran $99,50 al banco y se queda $0,50 de fee
registrar("settle:po_1", [("banco", "D", 9950),
                          ("gastos:fee_psp", "D", 50),
                          ("psp_por_cobrar", "C", 10000)])
# payout a Juan
registrar("payout:juan:2026-11", [("vendedor:juan", "D", 9700), ("banco", "C", 9700)])

try:
    registrar("bug", [("banco", "D", 100), ("vendedor:juan", "C", 99)])
except TransaccionDesbalanceada as e:
    print("rechazada:", e)

for cuenta in TIPO_CUENTA:
    print(cuenta, saldo(cuenta))
total_d = sum(a["monto"] for a in asientos if a["lado"] == "D")
total_c = sum(a["monto"] for a in asientos if a["lado"] == "C")
print("debe == haber:", total_d == total_c)
