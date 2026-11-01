DIAS_RETENCION = 7
MINIMO = 1000            # no pagar menos de $10

# cobros acreditados por vendedor (monto, día en que se cobró)
movimientos = {
    "juan": [(9700, 1), (4850, 5), (2000, 9)],
    "ana":  [(500, 2)],
    "leo":  [(30000, 1)],
}
kyc_ok = {"juan": True, "ana": True, "leo": False}
pagado = {"juan": 0, "ana": 0, "leo": 0}
payouts = {}             # UNIQUE por id

def disponible(vendedor, hoy):
    liberado = sum(m for m, dia in movimientos[vendedor] if hoy - dia >= DIAS_RETENCION)
    return liberado - pagado[vendedor]

def banco_transferir(id_payout, vendedor, monto):
    return "rebotó" if vendedor == "ana" else "ok"

def job_payouts(hoy):
    for vendedor in movimientos:
        id_payout = "payout:" + vendedor + ":" + str(hoy)
        if id_payout in payouts:
            print("  ", id_payout, "ya existe, no se paga de nuevo")
            continue
        monto = disponible(vendedor, hoy)
        if not kyc_ok[vendedor]:
            print("  ", vendedor, "sin KYC, retenido", monto)
            continue
        if monto < MINIMO:
            print("  ", vendedor, "debajo del mínimo:", monto)
            continue
        # BEGIN: crear payout + debitar saldo
        payouts[id_payout] = {"monto": monto, "status": "SENT"}
        pagado[vendedor] += monto
        # COMMIT
        r = banco_transferir(id_payout, vendedor, monto)
        if r == "ok":
            payouts[id_payout]["status"] = "PAID"
        else:
            payouts[id_payout]["status"] = "FAILED"
            pagado[vendedor] -= monto           # devolver el saldo
        print("  ", id_payout, monto, payouts[id_payout]["status"])

print("job día 12:")
job_payouts(12)
print("job día 12 (se corrió dos veces):")
job_payouts(12)
print("pagado:", pagado)
