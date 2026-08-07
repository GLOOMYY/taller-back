"""Health endpoint tests."""

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ruta_protegida_sin_token_devuelve_contrato_seguro() -> None:
    response = client.get("/api/v1/talleres")

    assert response.status_code == 401
    assert response.json()["codigo"] == "no_autenticado"
    assert response.json()["correlacion_id"] == response.headers["X-Correlation-ID"]


def test_readiness_falla_si_mongodb_no_esta_disponible(
    monkeypatch: MonkeyPatch,
) -> None:
    async def no_disponible(cliente: object) -> bool:
        del cliente
        return False

    monkeypatch.setattr("app.main.comprobar_mongodb", no_disponible)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["codigo"] == "no_disponible"
