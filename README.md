# Payment System (Sistema de pagos)

Un sistema de pagos es lo que **mueve plata** de una cuenta a otra y deja registrado cada movimiento. En un e-commerce tipo Amazon o Mercado Libre se encarga de cobrarle al comprador (**pay-in**), guardar cuánto le debe la plataforma a cada vendedor (**wallet**) y pagarle a los vendedores (**pay-out**).

```
Comprador ──pay-in──► [ Plataforma (cuenta del e-commerce) ] ──pay-out──► Vendedor
   tarjeta              ledger + wallet: "le debo $97 a Juan"              cuenta bancaria
```

A diferencia de casi cualquier otro sistema, acá **la performance no es lo importante, la corrección sí**. 1 millón de transacciones por día son ~12 por segundo: cualquier Postgres las aguanta. Lo difícil es que **ni un centavo se pierda ni se cobre dos veces**, aunque se caigan servicios, se corten conexiones o el usuario apriete "Pagar" cinco veces.

## Para qué sirve

- **Cobrar** al comprador con tarjeta, transferencia, billetera (PayPal, Mercado Pago, Apple/Google Pay), efectivo (Rapipago, Boleto, OXXO), etc.
- **Registrar** cada movimiento de plata de forma auditable (ledger de doble entrada).
- **Llevar el saldo** de cada vendedor (wallet).
- **Pagar** a los vendedores (payouts), descontando comisiones.
- **Devolver** (refunds) y **defenderse** de contracargos (chargebacks).
- **Conciliar**: comparar lo que dice nuestro sistema con lo que dicen el PSP y el banco, y detectar diferencias.

## Actores

```
           ┌─────────────── el mundo de la tarjeta ────────────────┐
Comprador ─► Comercio ─► PSP / Gateway ─► Adquirente ─► Red (Visa/MC) ─► Emisor (banco del comprador)
                         (Stripe, Adyen,   (banco del                       "¿tiene saldo? ¿es fraude?"
                          Mercado Pago)     comercio)
```

| Actor | Qué hace |
|---|---|
| **Comprador (payer)** | Quien paga. |
| **Comercio / vendedor (merchant, payee)** | Quien cobra. En un marketplace hay muchos vendedores detrás de una plataforma. |
| **PSP** (*Payment Service Provider*) | Stripe, Adyen, Braintree, Mercado Pago. Te abstrae de todo lo de abajo con una API. |
| **Adquirente** (*acquirer*) | Banco que tiene la cuenta del comercio y procesa sus cobros con tarjeta. |
| **Red / Card scheme** | Visa, Mastercard, Amex. Rutean la autorización entre adquirente y emisor y definen las reglas (y las disputas). |
| **Emisor** (*issuer*) | Banco que le dio la tarjeta al comprador. Aprueba o rechaza. |

## Conceptos clave

| Concepto | Qué es |
|---|---|
| **Pay-in** | Cobrar: la plata entra del comprador a la cuenta de la plataforma. |
| **Pay-out** | Pagar: la plata sale de la plataforma a la cuenta del vendedor. |
| **Payment event / checkout** | Un "Pagar" del usuario. Puede contener varias órdenes (un carrito con 3 vendedores). |
| **Payment order** | Un cobro individual (un vendedor, un monto). Es lo que se ejecuta contra el PSP. |
| **Autorización (auth)** | El emisor **reserva** el monto en la tarjeta. Todavía no se movió plata. Vence (~7 días). |
| **Captura (capture)** | Se confirma el cobro de una autorización. Ahí sí se va a mover la plata. |
| **Void** | Cancelar una autorización antes de capturar (no le cuesta nada al comprador). |
| **Settlement / liquidación** | El movimiento real de plata entre bancos. Pasa en batch, días después de la captura. |
| **Refund** | Devolución iniciada por el comercio. |
| **Chargeback / contracargo** | Devolución forzada por el banco del comprador ("yo no hice esta compra"). |
| **Ledger** | Libro contable inmutable con **todos** los movimientos, en doble entrada. Es la fuente de verdad. |
| **Wallet** | Saldo de cada cuenta (vendedor). Se puede derivar del ledger. |
| **Idempotency key** | Id único que manda el cliente para que repetir el mismo request no cobre dos veces. |
| **Reconciliación** | Comparar nuestros registros con los del PSP/banco (archivo de settlement) y encontrar diferencias. |
| **Webhook** | El PSP nos avisa por HTTP cuando cambia el estado de un pago. |
| **Tokenización** | Cambiar el número de tarjeta (PAN) por un token. Así nunca tocamos datos de tarjeta. |
| **PCI DSS** | Norma de seguridad obligatoria para quien guarda, procesa o transmite datos de tarjeta. |
| **3DS** (*3-D Secure*) | Paso extra donde el banco le pide al comprador que confirme (app, SMS). Pasa la responsabilidad del fraude al emisor. |
| **Minor units** | Guardar la plata como entero en la unidad mínima (centavos): `1050` = $10,50. |

### Garantías que necesitamos

| Garantía | Qué significa | Cómo se logra |
|---|---|---|
| **At-least-once** | Todo pago se intenta hasta tener un resultado. | Retries + estado persistido + jobs que retoman pagos colgados. |
| **At-most-once** | Nunca se cobra dos veces lo mismo. | Idempotency keys en **cada** salto (cliente→nosotros, nosotros→PSP, eventos→ledger/wallet). |
| **Exactly-once** | Las dos a la vez. | at-least-once + idempotencia. No existe "gratis" en la red. |
| **Consistencia** | Ledger, wallet, PSP y banco cuentan la misma historia. | Transacciones ACID donde se puede, outbox + eventos idempotentes entre servicios, y **reconciliación** para lo que se escapa. |

> Regla de oro: **un timeout no es un fallo, es un "no sé"**. Antes de reintentar un cobro, preguntá qué pasó.

## Requisitos (versión entrevista)

- **Funcionales**: pay-in (cobrar en nombre de los vendedores), pay-out (pagarles), refunds, consulta de estado.
- **No funcionales**: confiabilidad y tolerancia a fallos, consistencia fuerte en el dinero, auditabilidad, seguridad (PCI), reconciliación con sistemas externos.
- **Estimación**: 1M transacciones/día ≈ 12 TPS (picos de Black Friday ×10–×50 ≈ 600 TPS). No es un problema de throughput; es un problema de **correctitud**.

## Diseño de alto nivel

```
                                  ┌──────────── Risk / Fraude
                                  │
Cliente ──POST /payments──► Payment Service ──► Payment Executor ──► PSP ──► Red ──► Emisor
 (idempotency-key)            │   (DB: events,     (DB: orders,        │
                              │    orders)          psp_token)         │ webhook (async)
                              │                                        ▼
                              │◄──────────────────────── Webhook handler
                              │
                              └─ outbox ──► broker (pago.exitoso) ──┬──► Ledger   (doble entrada)
                                                                    ├──► Wallet   (saldo vendedor)
                                                                    └──► Notificaciones, analytics

Batch nocturno:  archivo de settlement del PSP ──► Reconciliación ──► diferencias ──► equipo de finanzas
Pay-out:         Wallet ──► Payout Service ──► proveedor de payouts / banco ──► Vendedor
```

**Flujo pay-in típico:**

1. El usuario aprieta "Pagar". El front manda `POST /v1/payments` con un `Idempotency-Key`.
2. **Payment Service** guarda el `payment_event` y sus `payment_orders` en estado `NOT_STARTED` (si la key ya existe, devuelve lo que ya había).
3. Chequeo de riesgo (fraude, AML, listas de sanciones).
4. **Payment Executor** pasa la orden a `EXECUTING` y llama al PSP mandando el `payment_order_id` como idempotency key del PSP.
5. El PSP responde (o no, o tarda, o responde después por webhook).
6. Se guarda el resultado y, **en la misma transacción**, un evento en la outbox.
7. **Ledger** y **Wallet** consumen el evento (de forma idempotente) y registran el movimiento.
8. Un job revisa órdenes colgadas en `EXECUTING` y consulta al PSP. De noche, la reconciliación compara todo con el settlement.

### API

```http
POST /v1/payments
Idempotency-Key: 6f1c2b7e-...
{
  "checkout_id": "chk_123",
  "buyer_id": "usr_9",
  "payment_method_token": "pm_tok_abc",     ← token del PSP, nunca la tarjeta
  "payment_orders": [
    { "payment_order_id": "po_1", "seller_id": "sel_7", "amount": "31.50", "currency": "USD" },
    { "payment_order_id": "po_2", "seller_id": "sel_8", "amount": "12.00", "currency": "USD" }
  ]
}

GET  /v1/payments/{payment_order_id}          → estado de una orden
POST /v1/payments/{payment_order_id}/refunds  → devolución (también con Idempotency-Key)
POST /webhooks/psp                            → el PSP nos avisa cambios (firmado con HMAC)
```

- El `amount` va como **string** (o entero en centavos), **nunca** como float.
- `payment_order_id` lo genera nuestro sistema y es el idempotency key que le mandamos al PSP.

### Modelo de datos (SQL, ACID)

Para plata se elige una base relacional probada (Postgres, MySQL, Oracle) o una NewSQL con consenso (CockroachDB, Spanner, YugabyteDB): transacciones ACID, constraints, herramientas, y gente que la sabe operar.

```sql
payment_events (
  checkout_id       TEXT PRIMARY KEY,
  buyer_id          TEXT NOT NULL,
  idempotency_key   TEXT UNIQUE NOT NULL,
  request_hash      TEXT NOT NULL,       -- para detectar misma key con distinto body
  is_payment_done   BOOLEAN DEFAULT false,
  created_at        TIMESTAMPTZ
)

payment_orders (
  payment_order_id  TEXT PRIMARY KEY,    -- también es la idempotency key hacia el PSP
  checkout_id       TEXT REFERENCES payment_events,
  seller_id         TEXT NOT NULL,
  amount_minor      BIGINT NOT NULL CHECK (amount_minor > 0),   -- centavos
  currency          CHAR(3) NOT NULL,
  status            TEXT NOT NULL,       -- NOT_STARTED, EXECUTING, SUCCESS, FAILED, ...
  psp_payment_id    TEXT,                -- id que nos devolvió el PSP (para reconciliar)
  ledger_updated    BOOLEAN DEFAULT false,
  wallet_updated    BOOLEAN DEFAULT false,
  version           INT NOT NULL DEFAULT 0,   -- optimistic locking
  updated_at        TIMESTAMPTZ
)

ledger_entries (                         -- append-only: nunca UPDATE ni DELETE
  entry_id          BIGSERIAL PRIMARY KEY,
  transaction_id    TEXT NOT NULL,       -- agrupa las patas de un movimiento
  account_id        TEXT NOT NULL,
  direction         TEXT CHECK (direction IN ('DEBIT','CREDIT')),
  amount_minor      BIGINT NOT NULL CHECK (amount_minor > 0),
  currency          CHAR(3) NOT NULL,
  created_at        TIMESTAMPTZ
)

outbox (id BIGSERIAL, topic TEXT, payload JSONB, sent_at TIMESTAMPTZ NULL)
```

### Máquina de estados de una orden

```
NOT_STARTED ──► EXECUTING ──┬──► SUCCESS ──► (REFUNDED / PARTIALLY_REFUNDED / CHARGEBACK)
                            ├──► FAILED            (terminal: tarjeta rechazada, fondos, fraude)
                            ├──► PENDING ──► SUCCESS | FAILED   (3DS, revisión manual, pagos en efectivo)
                            └──► UNKNOWN ──► (consultar al PSP) ──► SUCCESS | FAILED
```

Las transiciones son **explícitas**: un `FAILED` nunca vuelve a `EXECUTING` por accidente, y un webhook viejo no puede pisar un `SUCCESS`.

### Ledger de doble entrada

Cada movimiento afecta al menos dos cuentas, y la suma de débitos es igual a la suma de créditos. Si no cierra, hay un bug.

| Transacción | Cuenta | Débito | Crédito |
|---|---|---|---|
| Cobro de $100 | `psp_por_cobrar` | 100 | |
| | `vendedor:juan` | | 97 |
| | `ingresos:comision` | | 3 |
| Settlement del PSP (llegan $99,50, $0,50 de fee) | `banco` | 99,50 | |
| | `gastos:fee_psp` | 0,50 | |
| | `psp_por_cobrar` | | 100 |
| Payout a Juan | `vendedor:juan` | 97 | |
| | `banco` | | 97 |

El ledger es **append-only**: los errores se corrigen con asientos de reversa, nunca editando filas.

## Tipos / patrones

### 1. Integración con el PSP
- **API directa**: tu backend manda los datos de la tarjeta al PSP. Más control, pero entrás en alcance PCI pesado.
- **Hosted payment page / campos embebidos** (Stripe Checkout, Elements, Adyen Drop-in): la tarjeta la carga el usuario en un iframe/página del PSP. Vos solo ves un token. Lo que hace casi todo el mundo.
- **Directo con adquirente/redes**: solo empresas gigantes (Amazon, Uber) que justifican el costo y la certificación.

### 2. Flujo de cobro
- **Un paso (sale / auto-capture)**: autoriza y captura junto. Bienes digitales.
- **Dos pasos (auth + capture)**: reservás al comprar, capturás al despachar. Hoteles, rent-a-car, retail con stock incierto.

### 3. Sync vs async
- **Síncrono**: el cliente espera la respuesta del PSP. Simple, pero si el PSP tarda, todo tarda.
- **Asíncrono**: aceptás el pago (`202 PENDING`), lo procesás por detrás y avisás por webhook/polling/email. Necesario para 3DS, efectivo, transferencias y revisiones de fraude.

### 4. Consistencia entre servicios
- **Outbox + eventos idempotentes**: el estado y el evento se guardan juntos; ledger y wallet consumen con dedup.
- **Saga**: pasos con compensación (si falla el envío, se hace refund).
- **Reconciliación**: la red de seguridad final para todo lo demás.

## Errores comunes

### 1. Usar float para la plata
`0.1 + 0.2 = 0.30000000000000004`. Multiplicás por miles de transacciones y el ledger no cierra.
→ Enteros en centavos (`BIGINT`) o `Decimal` con redondeo explícito.

### 2. No tener idempotency key (doble click)
El usuario aprieta "Pagar" dos veces, o el front reintenta: dos cobros.
→ `Idempotency-Key` del cliente + `UNIQUE` en la DB + mismo id hacia el PSP.

### 3. Tratar un timeout como un fallo
El PSP cobró pero la respuesta se perdió. Marcás `FAILED`, el usuario reintenta y lo cobrás de nuevo.
→ Timeout = `UNKNOWN`. Consultar al PSP (con el mismo id) antes de decidir.

### 4. Race condition en el saldo
Dos procesos leen saldo $100, cada uno descuenta $80 y escribe: se pagaron $160 de una cuenta con $100.
→ `SELECT ... FOR UPDATE`, `UPDATE ... SET saldo = saldo - x WHERE saldo >= x`, o optimistic locking con `version`.

### 5. Ledger mutable
Corregir un error con `UPDATE ledger SET amount = ...`. Se pierde la historia y la auditoría.
→ Append-only. Errores se corrigen con asientos de reversa.

### 6. Confiar en el redirect del navegador
Marcar el pago como exitoso porque el usuario volvió a `/success?status=ok`. Cualquiera puede escribir esa URL.
→ La verdad viene del webhook firmado o de consultar la API del PSP, server-to-server.

### 7. Webhooks sin verificar la firma
Cualquiera puede hacer `POST /webhooks/psp {"status":"succeeded"}` y obtener la compra gratis.
→ Verificar el HMAC con el secreto del PSP, comparar en tiempo constante, rechazar timestamps viejos.

### 8. Webhooks duplicados y desordenados
El PSP reintenta webhooks y no garantiza orden: llega `succeeded`, después un `processing` viejo pisa el estado.
→ Dedup por `event_id` y solo transiciones válidas de la máquina de estados.

### 9. Dual write: PSP y DB por separado
Cobrás en el PSP y después guardás en la DB. Si la DB falla, le sacaste plata al usuario y no hay registro.
→ Guardar la intención **antes** (`EXECUTING`) con el id que va al PSP; job que retoma colgados; reconciliación.

### 10. Guardar o loguear datos de tarjeta
Un `logger.info(request.body)` con el número de tarjeta te mete en alcance PCI completo (y en un incidente).
→ Tokenización, hosted fields, y enmascarar/redactar logs.

### 11. Estados sin control
Cualquier código puede hacer `status = 'SUCCESS'`. Un pago `FAILED` pasa a `SUCCESS` sin que nadie cobre.
→ Máquina de estados explícita con transiciones válidas, y `UPDATE ... WHERE status = <esperado>`.

### 12. No conciliar
Asumir que si el código anda, la plata cuadra. Los PSP cobran fees que no esperabas, hay settlements que no llegan, refunds manuales.
→ Reconciliación diaria contra el settlement del PSP y el extracto del banco, con alertas.

### 13. Perder centavos al dividir
Dividir $100 en 3 cuotas → 33,33 × 3 = 99,99. ¿Dónde está el centavo?
→ Repartir el resto (*allocation*): 33,34 + 33,33 + 33,33.

### 14. Leer el estado desde una réplica
La réplica tiene lag: el pago ya es `SUCCESS` en el primario pero la réplica dice `NOT_STARTED`. El usuario vuelve a pagar.
→ Lecturas de dinero contra el primario (o read-your-writes / consenso).

### 15. Refund mayor que lo cobrado
Dos refunds concurrentes de $80 sobre un cobro de $100, o reembolsar algo que nunca se capturó.
→ Validar `refundado + nuevo <= capturado` con lock, e idempotency key en el refund.

### 16. Payout duplicado o sin saldo
El job de payouts corre dos veces (deploy, retry) y le paga dos veces al vendedor. O paga plata que todavía está en período de retención.
→ Payout idempotente por `(seller, período)`, débito del saldo en la misma transacción, saldo disponible ≠ saldo total.

### 17. Zonas horarias y cortes del día
Tu sistema corta el día en hora local, el PSP en UTC. La reconciliación del día "no cierra" todos los días.
→ Todo en UTC con `TIMESTAMPTZ`, y conciliar con la misma ventana que usa el PSP.

### 18. Reintentar todo
Reintentar un `card_declined` o `insufficient_funds` no lo arregla: suma fees, molesta al emisor y puede bloquear la tarjeta o al comercio.
→ Clasificar errores: reintentables (timeout, 5xx, rate limit) vs terminales (rechazo, fraude, datos inválidos).

### 19. No medir
Sin ver la tasa de aprobación, los pagos colgados en `EXECUTING`, la DLQ y las diferencias de conciliación, te enterás por los vendedores enojados.

## Cómo inspeccionar un sistema de pagos

```sql
-- Pagos colgados (deberían haber terminado hace rato)
SELECT payment_order_id, status, updated_at FROM payment_orders
WHERE status IN ('EXECUTING','UNKNOWN') AND updated_at < now() - interval '10 minutes';

-- El ledger tiene que cerrar: débitos = créditos por transacción
SELECT transaction_id,
       SUM(CASE WHEN direction='DEBIT' THEN amount_minor ELSE -amount_minor END) AS diferencia
FROM ledger_entries GROUP BY transaction_id
HAVING SUM(CASE WHEN direction='DEBIT' THEN amount_minor ELSE -amount_minor END) <> 0;

-- Pagos exitosos que no llegaron al ledger o a la wallet
SELECT * FROM payment_orders WHERE status='SUCCESS' AND (NOT ledger_updated OR NOT wallet_updated);

-- Tasa de aprobación por hora
SELECT date_trunc('hour', updated_at), AVG((status='SUCCESS')::int) FROM payment_orders GROUP BY 1;
```

```bash
# Stripe CLI: reenviar webhooks a tu local y disparar eventos de prueba
stripe listen --forward-to localhost:8000/webhooks/psp
stripe trigger payment_intent.succeeded
```

## Estructura

- [`implementaciones/`](implementaciones): cada pieza del sistema con un diagrama y código mínimo.
- [`errores/`](errores): cada error común, cómo se ve y cómo se arregla.

El código está en Python, solo con la librería estándar (nada de instalar paquetes). El foco está en el concepto, no en trucos del lenguaje.

```bash
python3 implementaciones/01-pay-in/pay_in.py
python3 errores/03-timeout-como-fallo/main.py
```

### Implementaciones

| # | Tema |
|---|---|
| 01 | [Pay-in de punta a punta](implementaciones/01-pay-in) |
| 02 | [Dinero en centavos y repartos](implementaciones/02-dinero-en-centavos) |
| 03 | [Máquina de estados](implementaciones/03-maquina-de-estados) |
| 04 | [Idempotency key en la API](implementaciones/04-idempotency-key) |
| 05 | [Ledger de doble entrada](implementaciones/05-ledger-doble-entrada) |
| 06 | [Wallet con locking](implementaciones/06-wallet-con-locking) |
| 07 | [Autorización y captura](implementaciones/07-autorizacion-y-captura) |
| 08 | [Hosted payment page + webhooks firmados](implementaciones/08-hosted-page-y-webhooks) |
| 09 | [Retries con backoff y DLQ](implementaciones/09-retry-y-dlq) |
| 10 | [Pagos pendientes y estado UNKNOWN](implementaciones/10-pendientes-y-unknown) |
| 11 | [Outbox: pago → ledger + wallet](implementaciones/11-outbox) |
| 12 | [Reconciliación](implementaciones/12-reconciliacion) |
| 13 | [Refunds y chargebacks](implementaciones/13-refunds-y-chargebacks) |
| 14 | [Payouts](implementaciones/14-payouts) |
| 15 | [Saga con compensación](implementaciones/15-saga) |
| 16 | [Tokenización y PCI](implementaciones/16-tokenizacion) |
| 17 | [Riesgo y fraude](implementaciones/17-riesgo-y-fraude) |
| 18 | [Routing multi-PSP y circuit breaker](implementaciones/18-multi-psp) |

### Errores

| # | Error |
|---|---|
| 01 | [Float para la plata](errores/01-float-para-dinero) |
| 02 | [Sin idempotency key (doble click)](errores/02-sin-idempotency-key) |
| 03 | [Timeout tratado como fallo](errores/03-timeout-como-fallo) |
| 04 | [Race condition en el saldo](errores/04-race-condition-saldo) |
| 05 | [Ledger mutable](errores/05-ledger-mutable) |
| 06 | [Confiar en el redirect](errores/06-confiar-en-el-redirect) |
| 07 | [Webhook sin firma](errores/07-webhook-sin-firma) |
| 08 | [Webhooks duplicados y desordenados](errores/08-webhooks-duplicados-y-desordenados) |
| 09 | [Dual write PSP / DB](errores/09-dual-write-psp-db) |
| 10 | [Guardar o loguear datos de tarjeta](errores/10-guardar-datos-de-tarjeta) |
| 11 | [Estados sin control](errores/11-estados-sin-control) |
| 12 | [No conciliar](errores/12-no-conciliar) |
| 13 | [Perder centavos al dividir](errores/13-perder-centavos-al-dividir) |
| 14 | [Leer de una réplica](errores/14-leer-de-replica) |
| 15 | [Refund mayor a lo cobrado](errores/15-refund-mayor-al-cobro) |
| 16 | [Payout duplicado o sin saldo](errores/16-payout-duplicado) |
| 17 | [Zonas horarias y cortes del día](errores/17-zonas-horarias) |
| 18 | [Reintentar todo](errores/18-reintentar-todo) |
| 19 | [No medir](errores/19-no-medir) |

## Más allá de la entrevista

- **Multi-moneda**: guardar siempre `(monto, moneda)`, tasa de cambio congelada en el momento del cobro, ledger por moneda (nunca sumar USD con ARS).
- **Métodos locales**: Pix (Brasil), UPI (India), efectivo (Rapipago, OXXO, Boleto) son **asíncronos** por naturaleza: el pago queda `PENDING` horas o días.
- **Apple Pay / Google Pay**: tokens de red (*network tokens*) en vez del PAN; mejoran la aprobación.
- **Suscripciones**: cobros recurrentes, reintentos inteligentes (*dunning*), actualización automática de tarjetas vencidas (*account updater*).
- **Regulación**: KYC de vendedores, AML, sanciones, impuestos y retenciones por país, retención de datos.
- **Observabilidad**: tasa de aprobación por PSP/emisor/país, latencia p99 del PSP, pagos colgados, tamaño de la DLQ, diferencias de conciliación, alertas.
- **Herramientas de debugging**: timeline de cada pago (requests, respuestas del PSP, webhooks, asientos) para que soporte entienda por qué falló.

## Plan del proyecto

La idea es armar un entorno local con Docker para ver cada concepto funcionando:

1. **Payment Service + Postgres**: `POST /payments` con idempotency key, tablas `payment_events`/`payment_orders` y máquina de estados.
2. **PSP falso**: un servicio que a veces aprueba, rechaza, tarda, devuelve timeout **después de cobrar**, y manda webhooks duplicados y desordenados.
3. **Ledger + Wallet**: consumidores de la outbox (vía RabbitMQ o Kafka) con dedup. Query que verifique que el ledger cierra.
4. **Stripe en modo test**: integración real con Checkout, webhooks con `stripe listen` y verificación de firma.
5. **Reconciliación**: generar un CSV de settlement del PSP falso y un job que encuentre diferencias.
6. **Payouts**: job diario idempotente que paga a los vendedores su saldo disponible.
7. **Romperla a propósito**: reproducir los errores de arriba (doble click, timeout tras cobrar, race en el saldo, webhook falso, réplica con lag) y arreglarlos.
