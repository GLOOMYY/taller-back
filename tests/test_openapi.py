"""Prueba del contrato compuesto, no solo routers aislados."""

from app.main import app


def test_openapi_publica_recursos_de_fases_uno_y_dos() -> None:
    paths = app.openapi()["paths"]

    assert {
        "/api/v1/usuarios/me",
        "/api/v1/talleres",
        "/api/v1/talleres/{taller_id}",
        "/api/v1/talleres/{taller_id}/miembros",
        "/api/v1/talleres/{taller_id}/miembros/{usuario_id}",
        "/api/v1/talleres/{taller_id}/clientes",
        "/api/v1/talleres/{taller_id}/clientes/{cliente_id}",
        "/api/v1/talleres/{taller_id}/referencias/paises",
        "/api/v1/talleres/{taller_id}/referencias/monedas",
        "/api/v1/talleres/{taller_id}/tipos-dispositivo",
        "/api/v1/talleres/{taller_id}/marcas-dispositivo",
        "/api/v1/talleres/{taller_id}/modelos-dispositivo",
        "/api/v1/talleres/{taller_id}/tipos-servicio",
        "/api/v1/talleres/{taller_id}/clientes/{cliente_id}/dispositivos",
        "/api/v1/talleres/{taller_id}/ordenes",
        "/api/v1/talleres/{taller_id}/proveedores",
        "/api/v1/talleres/{taller_id}/repuestos",
        "/api/v1/talleres/{taller_id}/metodos-pago",
        "/api/v1/talleres/{taller_id}/ordenes/{orden_id}/pagos",
        "/api/v1/publico/seguimiento/{token}",
        "/api/v1/publico/seguimiento/{token}/comprobante.pdf",
        "/health/live",
        "/health/ready",
    } <= set(paths)
