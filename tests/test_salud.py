async def test_health_responde_ok_con_db_y_redis(cliente):
    r = await cliente.get("/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True, "db": True, "redis": True}


async def test_toda_respuesta_trae_trace_id(cliente):
    r = await cliente.get("/health")
    assert len(r.headers["X-Trace-Id"]) == 32


async def test_trace_id_del_cliente_se_respeta(cliente):
    r = await cliente.get("/health", headers={"X-Trace-Id": "abc123"})
    assert r.headers["X-Trace-Id"] == "abc123"
