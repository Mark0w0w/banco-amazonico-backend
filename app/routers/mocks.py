"""Endpoints FALSOS (mocks) para que el frontend avance desde el día 1.

Devuelven datos inventados con la misma forma que tendrán los reales (los esquemas de
app/schemas son el contrato). Se activan con MOCKS_ACTIVOS=true y se van reemplazando por los
routers reales: cuando un router real exista, se borra su mock de aquí.
"""

import asyncio
import json
import random
import time
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Request, status
from sse_starlette.sse import EventSourceResponse

from app.schemas.auth import (
    LoginEntrada,
    LoginSalida,
    TecladoSalida,
    TokenSalida,
    TotpEntrada,
)
from app.schemas.chat import ConversacionSalida, MensajeEntrada
from app.schemas.cuentas import CuentaSalida, MovimientoSalida

router = APIRouter(prefix="/api/v1", tags=["mocks"])

CUENTAS = [
    CuentaSalida(
        id_cuenta=1,
        tipo="Cuenta Simple Soles",
        moneda="PEN",
        numero="193-94829104-0-12",
        cci="002-193-009482910401-18",
        saldo_disponible=Decimal("4850.20"),
        principal=True,
    ),
    CuentaSalida(
        id_cuenta=2,
        tipo="Cuenta de Ahorros Dólares",
        moneda="USD",
        numero="193-81023941-1-05",
        cci="002-193-008102394111-05",
        saldo_disponible=Decimal("1240.00"),
        principal=False,
    ),
]


def _movimientos_falsos(id_cuenta: int) -> list[MovimientoSalida]:
    ahora = datetime.now(UTC)
    base = [
        ("cargo", "184.50", "Supermercados Metro", "Débito Tarjeta", "Procesado"),
        ("abono", "350.00", "Transferencia de Juan Pérez", "Yape Amazónico", "Abono"),
        ("cargo", "42.80", "Farmacias Inkafarma", "Compra POS", "Procesado"),
        ("cargo", "85.00", "Pago de Servicio Sedapal", "Banca Móvil", "Recibo 94812"),
        ("cargo", "200.00", "Retiro Cajero Automático", "ATM Jockey Plaza", "Efectivo"),
    ]
    moneda = "PEN" if id_cuenta == 1 else "USD"
    return [
        MovimientoSalida(
            id_movimiento=id_cuenta * 100 + i,
            tipo=tipo,
            monto=Decimal(monto),
            moneda=moneda,
            descripcion=descripcion,
            canal=canal,
            estado=estado,
            fecha=ahora - timedelta(hours=6 * i),
        )
        for i, (tipo, monto, descripcion, canal, estado) in enumerate(base)
    ]


# ---------- Autenticación ----------


@router.get("/auth/teclado")
async def teclado() -> TecladoSalida:
    orden = list(range(10))
    random.shuffle(orden)
    return TecladoSalida(orden=orden)


@router.post("/auth/login")
async def login(datos: LoginEntrada) -> LoginSalida:
    # Mock: cualquier clave distinta de 000000 es válida.
    if datos.clave == "000000":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "credenciales inválidas")
    return LoginSalida(token_mfa=f"mock-mfa-{uuid.uuid4().hex}", metodos_mfa=["totp", "biometria"])


@router.post("/auth/mfa/totp")
async def verificar_totp(datos: TotpEntrada) -> TokenSalida:
    # Mock: el código 123456 siempre funciona.
    if datos.codigo != "123456":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "código TOTP inválido")
    return TokenSalida(access_token=f"mock-jwt-{uuid.uuid4().hex}", expira_en_segundos=300)


# ---------- Banco ----------


@router.get("/cuentas")
async def listar_cuentas() -> list[CuentaSalida]:
    return CUENTAS


@router.get("/cuentas/{id_cuenta}/movimientos")
async def listar_movimientos(id_cuenta: int, limite: int = 20) -> list[MovimientoSalida]:
    if id_cuenta not in {c.id_cuenta for c in CUENTAS}:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "esa cuenta no existe")
    return _movimientos_falsos(id_cuenta)[:limite]


# ---------- Asistente IA ----------


@router.post("/chat/conversaciones", status_code=status.HTTP_201_CREATED)
async def crear_conversacion() -> ConversacionSalida:
    return ConversacionSalida(id_conversacion=uuid.uuid4().hex, version_modelo="mock-azul")


def _evento(nombre: str, datos: dict) -> dict:
    return {"event": nombre, "data": json.dumps(datos, ensure_ascii=False)}


async def _respuesta_falsa(texto: str, trace_id: str) -> AsyncIterator[dict]:
    inicio = time.perf_counter()
    texto_min = texto.lower()

    if "saldo" in texto_min or "cuánto tengo" in texto_min or "cuanto tengo" in texto_min:
        intencion, confianza, origen = "consultar_saldo", 0.99, "plantilla"
        respuesta = "Tu Cuenta Simple en Soles tiene un saldo disponible de S/ 4,850.20."
    elif "bloque" in texto_min and "tarjeta" in texto_min:
        intencion, confianza, origen = "bloquear_tarjeta", 0.99, "plantilla"
        respuesta = "Para proteger tus fondos, bloquearemos tu tarjeta terminada en 7890."
    elif "tasa" in texto_min or "plazo fijo" in texto_min:
        intencion, confianza, origen = "consulta_producto", 0.93, "llm"
        respuesta = (
            "Nuestra Cuenta Depósito a Plazo Fijo Digital a 360 días ofrece una TREA de 6.85 % "
            "en soles para montos desde S/ 500. Fuente: Tarifario 2026, anexo de tasas pasivas."
        )
    else:
        intencion, confianza, origen = "fuera_de_dominio", 0.42, "llm"
        respuesta = "No estoy seguro de haber entendido. Te conecto con un asesor."

    yield _evento(
        "meta",
        {"intencion": intencion, "confianza": confianza, "origen": origen, "trace_id": trace_id},
    )

    ttft_ms = None
    for palabra in respuesta.split(" "):
        await asyncio.sleep(0.03)  # simula el streaming del LLM
        if ttft_ms is None:
            ttft_ms = int((time.perf_counter() - inicio) * 1000)
        yield _evento("token", {"texto": palabra + " "})

    if intencion == "bloquear_tarjeta":
        yield _evento(
            "accion",
            {
                "id_accion": uuid.uuid4().hex,
                "tipo": "bloquear_tarjeta",
                "resumen": {"tarjeta": "•••• 7890", "tipo_bloqueo": "temporal"},
            },
        )
    if confianza < 0.80:
        yield _evento("derivar", {"asesor": "Martín Alvarado", "motivo": "confianza baja"})

    yield _evento(
        "done",
        {"ttft_ms": ttft_ms or 0, "latencia_total_ms": int((time.perf_counter() - inicio) * 1000)},
    )


@router.post("/chat/conversaciones/{id_conversacion}/mensajes")
async def enviar_mensaje(
    id_conversacion: str, datos: MensajeEntrada, request: Request
) -> EventSourceResponse:
    return EventSourceResponse(_respuesta_falsa(datos.texto, request.state.trace_id))
