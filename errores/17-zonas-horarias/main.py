from datetime import datetime, timedelta, timezone

BSAS = timezone(timedelta(hours=-3))

# pagos hechos el 1/11 a la noche en Buenos Aires
pagos = [
    ("po_1", datetime(2026, 11, 1, 10, 0, tzinfo=BSAS), 5000),
    ("po_2", datetime(2026, 11, 1, 22, 30, tzinfo=BSAS), 3000),
    ("po_3", datetime(2026, 11, 1, 23, 50, tzinfo=BSAS), 2000),
]

# el PSP corta el día en UTC
settlement_psp_1_nov = sum(m for _, t, m in pagos if t.astimezone(timezone.utc).date().isoformat() == "2026-11-01")

nuestro_1_nov_local = sum(m for _, t, m in pagos if t.date().isoformat() == "2026-11-01")
print("❌ nuestro 1/11 (hora local):", nuestro_1_nov_local, "| PSP 1/11 (UTC):", settlement_psp_1_nov,
      "-> diferencia", nuestro_1_nov_local - settlement_psp_1_nov)

nuestro_1_nov_utc = sum(m for _, t, m in pagos if t.astimezone(timezone.utc).date().isoformat() == "2026-11-01")
print("✅ nuestro 1/11 (UTC):       ", nuestro_1_nov_utc, "| PSP 1/11 (UTC):", settlement_psp_1_nov,
      "-> diferencia", nuestro_1_nov_utc - settlement_psp_1_nov)

for id_pago, t, _ in pagos:
    print("  ", id_pago, "local:", t.strftime("%d/%m %H:%M"), "| UTC:", t.astimezone(timezone.utc).strftime("%d/%m %H:%M"))
