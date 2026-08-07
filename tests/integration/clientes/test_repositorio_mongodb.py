"""Integración real del repositorio MongoDB de Clientes."""

import asyncio
import os
import uuid

import pytest

pymongo = pytest.importorskip(
    "pymongo", reason="Las pruebas MongoDB requieren la dependencia pymongo."
)

from pymongo import AsyncMongoClient  # noqa: E402
from pymongo.errors import PyMongoError  # noqa: E402

from app.modules.clientes.application.errores import (  # noqa: E402
    CursorClientesInvalido,
)
from app.modules.clientes.domain.entidades import Cliente  # noqa: E402
from app.modules.clientes.infrastructure.mongodb import (  # noqa: E402
    COLECCION_CLIENTES,
    RepositorioClientesMongo,
)
from app.shared.application.contexto import ContextoTaller  # noqa: E402

pytestmark = pytest.mark.integration


def contexto(taller_id: str) -> ContextoTaller:
    """Crea un contexto autorizado para el Taller de prueba."""
    return ContextoTaller(
        usuario_id=f"usuario-{taller_id}", taller_id=taller_id, rol="dueno"
    )


def test_repositorio_crud_paginacion_indices_y_aislamiento() -> None:
    """RF-CLI-001/002 y BR-007: verifica MongoDB real."""

    async def escenario() -> None:
        uri = os.getenv(
            "MONGODB_TEST_URI",
            "mongodb://localhost:27017/?replicaSet=rs0&directConnection=true",
        )
        cliente_mongo = AsyncMongoClient(uri, serverSelectionTimeoutMS=500)
        try:
            try:
                await cliente_mongo.admin.command("ping")
            except PyMongoError as error:
                pytest.skip(f"MongoDB no disponible para integración: {error}")

            base_datos = cliente_mongo["taller_test"]
            repositorio = RepositorioClientesMongo(base_datos)
            sufijo = uuid.uuid4().hex
            contexto_a = contexto(f"taller-a-{sufijo}")
            contexto_b = contexto(f"taller-b-{sufijo}")
            coleccion = base_datos[COLECCION_CLIENTES]
            try:
                await repositorio.crear_indices()
                primero = await repositorio.crear(
                    contexto_a,
                    Cliente.nuevo(
                        taller_id=contexto_a.taller_id,
                        nombre="Ana",
                        telefono="123",
                    ),
                )
                segundo = await repositorio.crear(
                    contexto_a,
                    Cliente.nuevo(taller_id=contexto_a.taller_id, nombre="Ada"),
                )
                ajeno = await repositorio.crear(
                    contexto_b,
                    Cliente.nuevo(taller_id=contexto_b.taller_id, nombre="Beto"),
                )
                assert primero.id and segundo.id and ajeno.id

                pagina_1 = await repositorio.listar(contexto_a, limite=1, cursor=None)
                assert len(pagina_1.items) == 1
                assert pagina_1.siguiente_cursor is not None
                pagina_2 = await repositorio.listar(
                    contexto_a, limite=1, cursor=pagina_1.siguiente_cursor
                )
                assert len(pagina_2.items) == 1
                assert pagina_2.siguiente_cursor is None

                assert await repositorio.obtener(contexto_a, ajeno.id) is None
                with pytest.raises(ValueError):
                    await repositorio.actualizar(contexto_a, ajeno)
                with pytest.raises(CursorClientesInvalido):
                    await repositorio.listar(
                        contexto_b,
                        limite=20,
                        cursor=pagina_1.siguiente_cursor,
                    )

                actualizado = await repositorio.actualizar(
                    contexto_a,
                    Cliente(
                        id=primero.id,
                        taller_id=contexto_a.taller_id,
                        nombre="Ana María",
                        telefono=None,
                    ),
                )
                assert actualizado is not None
                assert actualizado.nombre == "Ana María"
                assert actualizado.telefono is None

                indices = await coleccion.index_information()
                assert "clientes_por_taller_id" in indices
                assert indices["clientes_por_taller_id"]["key"] == [
                    ("taller_id", 1),
                    ("_id", 1),
                ]
            finally:
                await coleccion.delete_many(
                    {"taller_id": {"$in": [contexto_a.taller_id, contexto_b.taller_id]}}
                )
        finally:
            await cliente_mongo.close()

    asyncio.run(escenario())
