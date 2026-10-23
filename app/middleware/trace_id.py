"""Asigna un trace_id a cada petición; sirve como evidencia en los reportes de defectos."""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

CABECERA = "X-Trace-Id"


class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = request.headers.get(CABECERA) or uuid.uuid4().hex
        request.state.trace_id = trace_id
        respuesta = await call_next(request)
        respuesta.headers[CABECERA] = trace_id
        return respuesta
