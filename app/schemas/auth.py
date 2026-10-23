from typing import Literal

from pydantic import BaseModel, Field


class TecladoSalida(BaseModel):
    """Orden aleatorio de los dígitos del teclado numérico (anti-keylogger)."""

    orden: list[int] = Field(min_length=10, max_length=10)


class LoginEntrada(BaseModel):
    tipo_documento: Literal["DNI", "CE", "RUC"]
    numero_documento: str = Field(pattern=r"^\d{8,12}$")
    numero_tarjeta: str = Field(pattern=r"^\d{13,19}$")
    clave: str = Field(pattern=r"^\d{6}$")


class LoginSalida(BaseModel):
    """Primer paso: la clave fue correcta, falta el segundo factor."""

    token_mfa: str
    requiere_mfa: bool = True
    metodos_mfa: list[Literal["totp", "biometria"]]


class TotpEntrada(BaseModel):
    token_mfa: str
    codigo: str = Field(pattern=r"^\d{6}$")


class TokenSalida(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105 — tipo de token, no una clave
    expira_en_segundos: int
