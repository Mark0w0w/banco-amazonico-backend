"""Configuración leída de variables de entorno (.env en local, panel del hosting en producción).

Si falta una variable obligatoria, la app no arranca y lo dice al instante.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Aplicación
    ENTORNO: Literal["desarrollo", "pruebas", "produccion"] = "desarrollo"
    DEBUG: bool = False
    MOCKS_ACTIVOS: bool = False

    # Base de datos y Redis (obligatorias: sin valor por defecto)
    DATABASE_URL: str
    DATABASE_URL_TEST: str | None = None
    REDIS_URL: str

    # Seguridad (RNF-03)
    JWT_SECRETO: str
    JWT_MINUTOS: int = 5
    INACTIVIDAD_SEGUNDOS: int = 300

    # CORS: orígenes separados por coma
    CORS_ORIGENES: str = "http://localhost:5173"

    # IA (Backend 2). Si falta, queda en "falso": no depende de GPU.
    LLM_PROVEEDOR: Literal["falso", "ollama"] = "falso"
    OLLAMA_URL: str = "http://host.docker.internal:11434"
    LLM_MODELO: str = "llama3.1:8b"
    EMBEDDINGS_MODELO: str = "bge-m3"

    @property
    def cors_origenes(self) -> list[str]:
        return [origen.strip() for origen in self.CORS_ORIGENES.split(",") if origen.strip()]


@lru_cache
def obtener_settings() -> Settings:
    return Settings()


settings = obtener_settings()
