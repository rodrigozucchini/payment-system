import threading
import time

def correr(funcion):
    cobro = {"capturado": 10000, "refundado": 0}
    devuelto = []
    hilos = [threading.Thread(target=funcion, args=(cobro, devuelto, 8000)) for _ in range(2)]
    for h in hilos: h.start()
    for h in hilos: h.join()
    return sum(devuelto)

def refund_mal(cobro, devuelto, monto):
    if cobro["refundado"] + monto <= cobro["capturado"]:
        time.sleep(0.01)                     # llamada al PSP
        cobro["refundado"] += monto
        devuelto.append(monto)

lock = threading.Lock()
def refund_bien(cobro, devuelto, monto):
    with lock:                               # SELECT ... FOR UPDATE
        if cobro["refundado"] + monto > cobro["capturado"]:
            return
        cobro["refundado"] += monto          # se reserva antes de llamar al PSP
    time.sleep(0.01)
    devuelto.append(monto)

print("❌ cobro 10000, dos refunds de 8000 ->  devuelto:", correr(refund_mal))
print("✅ cobro 10000, dos refunds de 8000 ->  devuelto:", correr(refund_bien))
