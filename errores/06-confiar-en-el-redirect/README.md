# Confiar en el redirect del navegador

Después de pagar en la página del PSP, el usuario vuelve a `https://tienda.com/success?order=123&status=approved`. Si tu backend marca el pedido como pagado porque llegó ese request, cualquiera puede escribir la URL a mano y llevarse el producto gratis.

Además, el redirect **puede no llegar nunca**: el usuario cierra la pestaña, se le corta internet, el banco del 3DS falla. Si dependés del redirect, tenés pagos cobrados que nunca marcaste.

```
❌ GET /success?status=approved ─► pedido.pagado = true
✅ GET /success?session=cs_123  ─► mostrar "procesando..."  (o consultar al PSP server-to-server)
   POST /webhooks/psp (firmado) ─► verificar firma ─► pedido.pagado = true
```

**Fix:** el redirect es solo UX. La verdad viene de:
- el **webhook firmado** del PSP, o
- una consulta **server-to-server** a la API del PSP con el id de la sesión (`GET /v1/checkout/sessions/cs_123`), verificando monto, moneda y que corresponda a ese pedido.
