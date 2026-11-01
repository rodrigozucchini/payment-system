import threading
import time

wallets = {"juan": {"disponible": 10000, "version": 0}}
lock_fila = threading.Lock()     # simula el lock de fila de la DB (SELECT ... FOR UPDATE)
pagados = []

# Opción 1: update atómico con condición (WHERE saldo >= monto)
def debitar_atomico(seller, monto):
    with lock_fila:              # la DB hace esto por nosotros en un solo UPDATE
        w = wallets[seller]
        if w["disponible"] < monto:
            return False
        w["disponible"] -= monto
        return True

# Opción 2: optimistic locking con version
def debitar_optimista(seller, monto, intentos=5):
    for _ in range(intentos):
        w = wallets[seller]
        leida_version = w["version"]
        leido_saldo = w["disponible"]
        time.sleep(0.001)                       # trabajo en el medio
        if leido_saldo < monto:
            return False
        with lock_fila:                         # UPDATE ... WHERE version = leida_version
            if w["version"] != leida_version:
                continue                        # 0 filas afectadas: reintentar
            w["disponible"] = leido_saldo - monto
            w["version"] += 1
            return True
    return False

def payout(funcion):
    if funcion("juan", 8000):
        pagados.append(8000)

for funcion in (debitar_atomico, debitar_optimista):
    wallets["juan"] = {"disponible": 10000, "version": 0}
    pagados.clear()
    hilos = [threading.Thread(target=payout, args=(funcion,)) for _ in range(5)]
    for h in hilos: h.start()
    for h in hilos: h.join()
    print(funcion.__name__, "pagados:", pagados, "saldo:", wallets["juan"]["disponible"])
