from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

Moneda = Literal["PEN", "USD"]


class CuentaSalida(BaseModel):
    id_cuenta: int
    tipo: str
    moneda: Moneda
    numero: str
    cci: str
    saldo_disponible: Decimal
    principal: bool


class MovimientoSalida(BaseModel):
    id_movimiento: int
    tipo: Literal["cargo", "abono"]
    monto: Decimal
    moneda: Moneda
    descripcion: str
    canal: str
    estado: str
    fecha: datetime
