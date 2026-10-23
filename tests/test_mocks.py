"""Contrato de los mocks: si cambia la forma de una respuesta, el frontend se entera aquí."""

import json

LOGIN_VALIDO = {
    "tipo_documento": "DNI",
    "numero_documento": "47891234",
    "numero_tarjeta": "4557000000008912",
    "clave": "482913",
}


async def test_teclado_trae_los_10_digitos_sin_repetir(cliente):
    r = await cliente.get("/api/v1/auth/teclado")
    assert sorted(r.json()["orden"]) == list(range(10))


async def test_login_valido_pide_mfa(cliente):
    r = await cliente.post("/api/v1/auth/login", json=LOGIN_VALIDO)
    assert r.status_code == 200
    assert r.json()["requiere_mfa"] is True


async def test_login_con_clave_de_5_digitos_da_422(cliente):
    r = await cliente.post("/api/v1/auth/login", json={**LOGIN_VALIDO, "clave": "12345"})
    assert r.status_code == 422


async def test_totp_incorrecto_da_401(cliente):
    r = await cliente.post("/api/v1/auth/mfa/totp", json={"token_mfa": "x", "codigo": "999999"})
    assert r.status_code == 401


async def test_cuentas_tienen_soles_y_dolares(cliente):
    r = await cliente.get("/api/v1/cuentas")
    assert {c["moneda"] for c in r.json()} == {"PEN", "USD"}


async def test_movimientos_de_cuenta_inexistente_da_404(cliente):
    r = await cliente.get("/api/v1/cuentas/999/movimientos")
    assert r.status_code == 404


async def _eventos_del_chat(cliente, texto: str) -> list[tuple[str, dict]]:
    conv = (await cliente.post("/api/v1/chat/conversaciones")).json()
    url = f"/api/v1/chat/conversaciones/{conv['id_conversacion']}/mensajes"
    eventos, nombre = [], None
    async with cliente.stream("POST", url, json={"texto": texto}) as r:
        async for linea in r.aiter_lines():
            if linea.startswith("event:"):
                nombre = linea.removeprefix("event:").strip()
            elif linea.startswith("data:"):
                eventos.append((nombre, json.loads(linea.removeprefix("data:").strip())))
    return eventos


async def test_chat_empieza_con_meta_y_termina_con_done(cliente):
    eventos = await _eventos_del_chat(cliente, "¿cuánto tengo en mi cuenta?")
    assert eventos[0][0] == "meta"
    assert eventos[0][1]["intencion"] == "consultar_saldo"
    assert eventos[-1][0] == "done"


async def test_chat_bloqueo_propone_accion(cliente):
    eventos = await _eventos_del_chat(cliente, "quiero bloquear mi tarjeta [TARJETA_1]")
    assert "accion" in [nombre for nombre, _ in eventos]


async def test_chat_con_confianza_baja_deriva(cliente):
    eventos = await _eventos_del_chat(cliente, "renegociar hipoteca con fideicomiso mixto")
    assert "derivar" in [nombre for nombre, _ in eventos]
