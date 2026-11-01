primario = {"po_1": "EXECUTING"}
replica = dict(primario)
pendientes_de_replicar = []

def escribir(id_orden, estado):
    primario[id_orden] = estado
    pendientes_de_replicar.append((id_orden, estado))     # llega a la réplica "después"

def replicar():
    while pendientes_de_replicar:
        k, v = pendientes_de_replicar.pop(0)
        replica[k] = v

cobros = []
def front_consulta_y_reintenta(leer_de):
    estado = leer_de["po_1"]
    if estado != "SUCCESS":
        cobros.append("po_1 reintento")          # el usuario ve "no se completó" y paga de nuevo
    return estado

cobros.append("po_1")
escribir("po_1", "SUCCESS")
print("❌ leyendo de la réplica:", front_consulta_y_reintenta(replica), "-> cobros:", cobros)

cobros = ["po_1"]
print("✅ leyendo del primario: ", front_consulta_y_reintenta(primario), "-> cobros:", cobros)
replicar()
print("   (un rato después la réplica dice:", replica["po_1"] + ")")
