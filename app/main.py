"""Punto de entrada: crea la app, registra middlewares y junta los routers."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.trace_id import TraceIdMiddleware
from app.routers import mocks, salud

app = FastAPI(
    title="Banco Amazónico — Asistente Virtual con IA",
    version="0.1.0",
    description="Backend del proyecto de Calidad de Sistemas (UNAMAD). RNF-01 a RNF-05.",
)

app.add_middleware(TraceIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origenes,  # nunca "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Trace-Id"],
)

app.include_router(salud.router)
if settings.MOCKS_ACTIVOS:
    app.include_router(mocks.router)
