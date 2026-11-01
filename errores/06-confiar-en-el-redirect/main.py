pedidos = {"123": {"monto": 50000, "pagado": False}, "124": {"monto": 50000, "pagado": False}}
psp_sesiones = {"cs_abc": {"pedido": "124", "monto": 50000, "status": "paid"}}   # lo que sabe el PSP

def success_mal(query):
    if query.get("status") == "approved":
        pedidos[query["order"]]["pagado"] = True

def success_bien(query):
    sesion = psp_sesiones.get(query.get("session"))     # GET al PSP, server-to-server
    if sesion is None:
        return "sesión desconocida"
    pedido = pedidos[sesion["pedido"]]
    if sesion["status"] == "paid" and sesion["monto"] == pedido["monto"]:
        pedido["pagado"] = True
        return "pagado (verificado con el PSP)"
    return "todavía no"

# un atacante escribe la URL a mano
success_mal({"order": "123", "status": "approved"})
print("❌ pedido 123 pagado:", pedidos["123"]["pagado"], "(nadie pagó nada)")

pedidos["123"]["pagado"] = False
print("✅", success_bien({"order": "123", "status": "approved"}), "->", pedidos["123"]["pagado"])
print("✅", success_bien({"session": "cs_abc"}), "->", pedidos["124"]["pagado"])
