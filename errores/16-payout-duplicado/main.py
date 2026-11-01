def correr_dos_veces(job):
    estado = {"saldo": 50000, "transferido": 0, "payouts": set()}
    job(estado, "2026-11-01")
    job(estado, "2026-11-01")            # segunda instancia del cron
    return estado["transferido"], estado["saldo"]

def job_mal(estado, fecha):
    estado["transferido"] += estado["saldo"]   # transfiere...
    # ...y se cae antes de debitar el saldo

def job_bien(estado, fecha):
    id_payout = "payout:juan:" + fecha
    if id_payout in estado["payouts"]:         # INSERT ... UNIQUE falla
        return
    monto = estado["saldo"]
    estado["payouts"].add(id_payout)           # BEGIN
    estado["saldo"] -= monto                   # (misma transacción)
    estado["transferido"] += monto             # COMMIT y después banco.transferir(id_payout)

print("❌ transferido, saldo restante:", correr_dos_veces(job_mal))
print("✅ transferido, saldo restante:", correr_dos_veces(job_bien))
