"""Configuración común de pytest.

Las pruebas usan la base DATABASE_URL_TEST (nunca la de desarrollo) y los mocks activos.
Estas variables se fijan ANTES de importar la app, porque la configuración se lee al importar.
"""

import os

if os.environ.get("DATABASE_URL_TEST"):
    os.environ["DATABASE_URL"] = os.environ["DATABASE_URL_TEST"]
os.environ["ENTORNO"] = "pruebas"
os.environ["MOCKS_ACTIVOS"] = "true"
os.environ["LLM_PROVEEDOR"] = "falso"

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
async def cliente():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
