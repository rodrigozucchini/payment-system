log = []

def reservar_stock(ctx):  log.append("stock reservado")
def liberar_stock(ctx):   log.append("stock liberado")
def autorizar_pago(ctx):  log.append("pago autorizado"); ctx["auth"] = "pi_1"
def anular_pago(ctx):     log.append("pago anulado (void " + ctx["auth"] + ")")
def capturar_pago(ctx):   log.append("pago capturado")
def crear_envio(ctx):
    if ctx["sin_cobertura"]:
        raise Exception("el correo no llega a ese código postal")
    log.append("envío creado")
def cancelar_envio(ctx):  log.append("envío cancelado")

PASOS = [
    (reservar_stock, liberar_stock),
    (autorizar_pago, anular_pago),
    (crear_envio, cancelar_envio),
    (capturar_pago, None),          # último: capturar recién cuando todo salió bien
]

def correr_saga(ctx):
    hechos = []
    for paso, compensacion in PASOS:
        try:
            paso(ctx)
            hechos.append(compensacion)        # en la vida real: persistir el estado de la saga
        except Exception as e:
            log.append("FALLÓ " + paso.__name__ + ": " + str(e))
            for comp in reversed(hechos):
                if comp:
                    comp(ctx)                  # con retries hasta que salga
            return "COMPENSADA"
    return "COMPLETADA"

print(correr_saga({"sin_cobertura": False}), log)
log.clear()
print(correr_saga({"sin_cobertura": True}))
for l in log: print("  ", l)
