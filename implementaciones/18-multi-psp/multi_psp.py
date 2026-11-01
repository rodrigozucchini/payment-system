UMBRAL = 3
ENFRIAMIENTO = 30

class Circuito:
    def __init__(self):
        self.errores = 0
        self.abierto_desde = None

    def disponible(self, ahora):
        if self.abierto_desde is None:
            return True
        return ahora - self.abierto_desde >= ENFRIAMIENTO     # semi-abierto: dejo pasar uno

    def exito(self):
        self.errores = 0
        self.abierto_desde = None

    def fallo(self, ahora):
        self.errores += 1
        if self.errores >= UMBRAL:
            self.abierto_desde = ahora

psps = {
    "psp_local":  {"aprobacion": 0.92, "fee": 3.5, "circuito": Circuito(), "caido": True},
    "psp_global": {"aprobacion": 0.85, "fee": 2.9, "circuito": Circuito(), "caido": False},
}

def llamar(nombre):
    if psps[nombre]["caido"]:
        return "connection_refused"       # seguro que no cobró: se puede hacer failover
    return "ok"

def rutear(id_pago, ahora):
    candidatos = sorted(psps, key=lambda n: -psps[n]["aprobacion"])   # el que más aprueba primero
    for nombre in candidatos:
        c = psps[nombre]["circuito"]
        if not c.disponible(ahora):
            continue
        r = llamar(nombre)
        if r == "ok":
            c.exito()
            return id_pago + " -> " + nombre
        if r == "timeout":
            return id_pago + " -> UNKNOWN en " + nombre + " (NO hacer failover)"
        c.fallo(ahora)                     # connection_refused / 503: failover al siguiente
    return id_pago + " -> sin PSP disponible"

for t in range(5):
    print("t=" + str(t), rutear("po_" + str(t), t), "| local abierto:", psps["psp_local"]["circuito"].abierto_desde is not None)

psps["psp_local"]["caido"] = False         # se recuperó
print("t=40", rutear("po_40", 40))          # semi-abierto: prueba y vuelve al local
