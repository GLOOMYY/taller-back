"""Pruebas unitarias del dominio de Clientes."""

import pytest

from app.modules.clientes.domain.entidades import CambiosCliente, Cliente
from app.modules.clientes.domain.errores import ClienteInvalido


def test_cliente_exige_nombre() -> None:
    """RF-CLI-001: el nombre es obligatorio."""
    with pytest.raises(ClienteInvalido):
        Cliente.nuevo(taller_id="taller-a", nombre="   ")


def test_cliente_permite_datos_opcionales() -> None:
    """RF-CLI-001: teléfono, correo y notas pueden omitirse."""
    cliente = Cliente.nuevo(taller_id="taller-a", nombre="  Ana  ")

    assert cliente.nombre == "Ana"
    assert cliente.telefono is None
    assert cliente.correo is None
    assert cliente.notas is None


def test_actualizacion_parcial_distingue_omitido_de_nulo() -> None:
    """RF-CLI-002: un opcional presente como null se elimina."""
    cliente = Cliente(
        id="cliente-1",
        taller_id="taller-a",
        nombre="Ana",
        telefono="123",
        correo="ana@example.test",
    )

    actualizado = cliente.actualizar(
        CambiosCliente(telefono_definido=True, telefono=None)
    )

    assert actualizado.telefono is None
    assert actualizado.correo == "ana@example.test"


def test_actualizacion_vacia_es_invalida() -> None:
    """RF-CLI-002: patch exige al menos un campo."""
    cliente = Cliente(id="cliente-1", taller_id="taller-a", nombre="Ana")

    with pytest.raises(ClienteInvalido):
        cliente.actualizar(CambiosCliente())
