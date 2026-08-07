"""Integración de atomicidad e invariantes multi-colección en MongoDB real."""

import asyncio
import os
from dataclasses import dataclass
from uuid import uuid4

import pytest
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from app.core.composition import UnidadCreacionTallerMongo
from app.modules.membresias.application.puertos import UsuarioReferencia
from app.modules.membresias.application.servicio import ServicioMembresias
from app.modules.membresias.domain.modelos import RolMembresia
from app.modules.membresias.infrastructure.mongo import RepositorioMembresiasMongo
from app.modules.talleres.domain.modelos import Taller
from app.modules.talleres.infrastructure.mongo import RepositorioTalleresMongo
from app.shared.application import Conflicto

pytestmark = pytest.mark.integration


@dataclass
class DirectorioVacio:
    async def buscar_por_nombre_usuario(
        self, nombre_usuario: str
    ) -> UsuarioReferencia | None:
        del nombre_usuario
        return None


def test_creacion_atomica_indices_y_ultimo_dueno() -> None:
    """RF-TAL-001/RF-MEM-004: comprueba transacciones sobre replica set."""

    async def escenario() -> None:
        uri = os.getenv(
            "MONGODB_TEST_URI",
            "mongodb://localhost:27017/?replicaSet=rs0&directConnection=true",
        )
        cliente = AsyncMongoClient(uri, serverSelectionTimeoutMS=500)
        try:
            try:
                await cliente.admin.command("ping")
            except PyMongoError as error:
                pytest.skip(f"MongoDB no disponible para integración: {error}")

            nombre_base = f"taller_test_{uuid4().hex}"
            base = cliente[nombre_base]
            talleres = RepositorioTalleresMongo(base["talleres"])
            repositorio_membresias = RepositorioMembresiasMongo(
                base["membresias"], cliente
            )
            membresias = ServicioMembresias(
                repositorio_membresias,
                DirectorioVacio(),
                lambda: str(uuid4()),
            )
            try:
                await repositorio_membresias.crear_indices()
                unidad = UnidadCreacionTallerMongo(
                    cliente, talleres, membresias, base["metodos_pago"]
                )
                async with unidad:
                    await unidad.guardar_taller(Taller("taller-ok", "Central"))
                    await unidad.crear_membresia_dueno("taller-ok", "usuario-1")
                    await unidad.crear_metodo_efectivo("taller-ok")

                assert await talleres.obtener("taller-ok") is not None
                creada = await repositorio_membresias.obtener("taller-ok", "usuario-1")
                assert creada is not None
                assert creada.rol is RolMembresia.DUENO
                assert await base["metodos_pago"].find_one(
                    {"taller_id": "taller-ok", "nombre_normalizado": "efectivo"}
                )

                with pytest.raises(Conflicto):
                    async with UnidadCreacionTallerMongo(
                        cliente, talleres, membresias, base["metodos_pago"]
                    ) as fallida:
                        await fallida.guardar_taller(
                            Taller("taller-rollback", "No visible")
                        )
                        await fallida.crear_membresia_dueno("taller-ok", "usuario-1")
                assert await talleres.obtener("taller-rollback") is None

                with pytest.raises(Conflicto):
                    await repositorio_membresias.cambiar_rol_protegiendo_ultimo_dueno(
                        "taller-ok", "usuario-1", RolMembresia.TECNICO
                    )
                indices = await base["membresias"].index_information()
                assert "uq_membresia_taller_usuario" in indices
            finally:
                await cliente.drop_database(nombre_base)
        finally:
            await cliente.close()

    asyncio.run(escenario())
