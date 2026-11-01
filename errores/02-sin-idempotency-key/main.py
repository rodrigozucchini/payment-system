import threading
import time

cobros = []

def pagar_mal(checkout_id, monto):
    cobros.append(monto)

claves_vistas = set()
def pagar_con_if(key, monto):
    if key in claves_vistas:          # check...
        return
    time.sleep(0.01)                  # ...el tiempo entre check y write
    claves_vistas.add(key)            # ...then act
    cobros.append(monto)

lock_db = threading.Lock()
claves_unique = set()
def pagar_bien(key, monto):
    with lock_db:                     # equivale a INSERT con UNIQUE: atómico
        if key in claves_unique:
            return
        claves_unique.add(key)
    cobros.append(monto)

def doble_click(funcion, *args):
    cobros.clear()
    hilos = [threading.Thread(target=funcion, args=args) for _ in range(2)]
    for h in hilos: h.start()
    for h in hilos: h.join()
    return sum(cobros)

print("❌ sin key:        cobrado", doble_click(pagar_mal, "chk_1", 5000))
print("❌ key con un if:  cobrado", doble_click(pagar_con_if, "k1", 5000))
print("✅ key con UNIQUE: cobrado", doble_click(pagar_bien, "k1", 5000))
