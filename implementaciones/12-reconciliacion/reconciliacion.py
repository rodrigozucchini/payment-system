import csv
import io

# lo que tenemos nosotros
nuestros = {
    "po_1": {"status": "SUCCESS", "monto": 10000},
    "po_2": {"status": "UNKNOWN", "monto": 5000},    # timeout, nunca supimos
    "po_3": {"status": "SUCCESS", "monto": 2000},    # el PSP no lo tiene
    "po_4": {"status": "SUCCESS", "monto": 8000},
    "po_5": {"status": "SUCCESS", "monto": 3000},
}

# archivo de settlement del PSP (fee incluido)
settlement_csv = """payment_order_id,tipo,monto,fee
po_1,charge,10000,320
po_2,charge,5000,175
po_4,charge,7000,230
po_5,charge,3000,117
po_5,refund,-3000,0
"""

def leer_settlement(texto):
    filas = {}
    for f in csv.DictReader(io.StringIO(texto)):
        filas.setdefault(f["payment_order_id"], []).append(f)
    return filas

def conciliar(nuestros, psp):
    diferencias = []
    for id_orden, o in nuestros.items():
        filas = psp.get(id_orden, [])
        cobrado = sum(int(f["monto"]) for f in filas if f["tipo"] == "charge")
        refundado = -sum(int(f["monto"]) for f in filas if f["tipo"] == "refund")
        if not filas and o["status"] == "SUCCESS":
            diferencias.append((id_orden, "FALTA_EN_PSP", "investigar"))
        elif filas and o["status"] in ("UNKNOWN", "FAILED", "EXECUTING"):
            diferencias.append((id_orden, "COBRADO_PERO_NO_LO_SABEMOS", "auto: pasar a SUCCESS + asiento"))
        elif cobrado and cobrado != o["monto"]:
            diferencias.append((id_orden, "MONTO_DISTINTO " + str(o["monto"]) + " vs " + str(cobrado), "manual: finanzas"))
        elif refundado:
            diferencias.append((id_orden, "REFUND_QUE_NO_CONOCEMOS", "auto: registrar refund + asiento"))
    for id_orden in psp:
        if id_orden not in nuestros:
            diferencias.append((id_orden, "DESCONOCIDO", "investigar"))
    return diferencias

psp = leer_settlement(settlement_csv)
for d in conciliar(nuestros, psp):
    print(d)

fees = sum(int(f["fee"]) for filas in psp.values() for f in filas)
print("fees del día a registrar en gastos:fee_psp:", fees)
