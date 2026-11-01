import threading
import time

saldo = {"juan": 10000}
pagos = []
lock = threading.Lock()

def payout_mal(monto):
    actual = saldo["juan"]               # SELECT saldo
    time.sleep(0.01)                     # llamada al banco, lógica, lo que sea
    if actual >= monto:
        saldo["juan"] = actual - monto   # UPDATE saldo = <valor calculado en la app>
        pagos.append(monto)

def payout_bien(monto):
    with lock:                           # UPDATE ... SET saldo = saldo - x WHERE saldo >= x
        if saldo["juan"] < monto:
            return
        saldo["juan"] -= monto
    pagos.append(monto)

for funcion, simbolo in ((payout_mal, "❌"), (payout_bien, "✅")):
    saldo["juan"] = 10000
    pagos.clear()
    hilos = [threading.Thread(target=funcion, args=(8000,)) for _ in range(3)]
    for h in hilos: h.start()
    for h in hilos: h.join()
    print(simbolo, "saldo inicial 10000 | pagado:", sum(pagos), "| saldo final:", saldo["juan"])
