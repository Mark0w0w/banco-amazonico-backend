"""Contrato del asistente. El streaming (SSE) emite estos eventos, en este orden:

meta    → MetaEvento         (siempre, primero)
token   → TokenEvento        (0..n fragmentos de texto)
accion  → AccionEvento       (si la IA propone una operación que requiere huella/TOTP)
derivar → DerivarEvento      (si la confianza < 0.80)
done    → DoneEvento         (siempre, al final)
"""

from pydantic import BaseModel, Field


class ConversacionSalida(BaseModel):
    id_conversacion: str
    version_modelo: str


class MensajeEntrada(BaseModel):
    # Ya enmascarado por la capa 1 del frontend (RNF-02); el backend vuelve a enmascarar.
    texto: str = Field(min_length=1, max_length=1000)


class MetaEvento(BaseModel):
    intencion: str
    confianza: float = Field(ge=0, le=1)
    origen: str  # "plantilla" | "cache" | "llm"
    trace_id: str


class TokenEvento(BaseModel):
    texto: str


class AccionEvento(BaseModel):
    id_accion: str
    tipo: str  # "transferir" | "bloquear_tarjeta"
    resumen: dict


class DerivarEvento(BaseModel):
    asesor: str
    motivo: str


class DoneEvento(BaseModel):
    ttft_ms: int
    latencia_total_ms: int
