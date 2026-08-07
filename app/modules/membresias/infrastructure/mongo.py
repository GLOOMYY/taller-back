"""Repositorio MongoDB tenant-aware para Membresías."""

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.modules.membresias.domain.modelos import Membresia, RolMembresia
from app.shared.application import Conflicto

ResultadoTransaccion = TypeVar("ResultadoTransaccion")


class RepositorioMembresiasMongo:
    """Persiste Membresías con IDs opacos y filtros por Taller."""

    def __init__(self, coleccion: Any, cliente: Any) -> None:
        self._coleccion = coleccion
        self._cliente = cliente

    async def crear_indices(self) -> None:
        """Crea restricciones y rutas de consulta requeridas."""
        await self._coleccion.create_index(
            [("taller_id", ASCENDING), ("usuario_id", ASCENDING)],
            unique=True,
            name="uq_membresia_taller_usuario",
        )
        await self._coleccion.create_index(
            [("usuario_id", ASCENDING), ("taller_id", ASCENDING)],
            name="ix_membresia_usuario_taller",
        )
        await self._coleccion.create_index(
            [("taller_id", ASCENDING), ("rol", ASCENDING)],
            name="ix_membresia_taller_rol",
        )

    async def obtener(self, taller_id: str, usuario_id: str) -> Membresia | None:
        documento = await self._coleccion.find_one(
            {"taller_id": taller_id, "usuario_id": usuario_id}
        )
        return self._a_dominio(documento) if documento else None

    async def listar(
        self, taller_id: str, limite: int, despues_de: str | None
    ) -> list[Membresia]:
        filtro: dict[str, Any] = {"taller_id": taller_id}
        if despues_de is not None:
            filtro["_id"] = {"$gt": despues_de}
        cursor = self._coleccion.find(filtro).sort("_id", ASCENDING).limit(limite)
        documentos = await cursor.to_list(length=limite)
        return [self._a_dominio(documento) for documento in documentos]

    async def listar_taller_ids(self, usuario_id: str) -> list[str]:
        """Lista IDs de Taller de las Membresías del Usuario."""
        cursor = self._coleccion.find(
            {"usuario_id": usuario_id}, {"_id": 0, "taller_id": 1}
        ).sort("taller_id", ASCENDING)
        documentos = await cursor.to_list(length=None)
        return [documento["taller_id"] for documento in documentos]

    async def crear(self, membresia: Membresia, session: object | None = None) -> None:
        documento = {
            "_id": membresia.id,
            "taller_id": membresia.taller_id,
            "usuario_id": membresia.usuario_id,
            "rol": membresia.rol.value,
        }
        try:
            await self._coleccion.insert_one(documento, session=session)
        except DuplicateKeyError as exc:
            raise Conflicto("El Usuario ya es miembro del Taller") from exc

    async def cambiar_rol_protegiendo_ultimo_dueno(
        self,
        taller_id: str,
        usuario_id: str,
        rol: RolMembresia,
    ) -> Membresia | None:
        async def operacion(session: Any) -> Membresia | None:
            filtro = {"taller_id": taller_id, "usuario_id": usuario_id}
            actual = await self._coleccion.find_one(filtro, session=session)
            if actual is None:
                return None
            if (
                actual["rol"] == RolMembresia.DUENO.value
                and rol is RolMembresia.TECNICO
            ):
                await self._exigir_otro_dueno(taller_id, session)
            actualizado = await self._coleccion.find_one_and_update(
                filtro,
                {"$set": {"rol": rol.value}},
                return_document=ReturnDocument.AFTER,
                session=session,
            )
            return self._a_dominio(actualizado) if actualizado else None

        return await self._en_transaccion(operacion)

    async def retirar_protegiendo_ultimo_dueno(
        self, taller_id: str, usuario_id: str
    ) -> bool:
        async def operacion(session: Any) -> bool:
            filtro = {"taller_id": taller_id, "usuario_id": usuario_id}
            actual = await self._coleccion.find_one(filtro, session=session)
            if actual is None:
                return False
            if actual["rol"] == RolMembresia.DUENO.value:
                await self._exigir_otro_dueno(taller_id, session)
            resultado = await self._coleccion.delete_one(filtro, session=session)
            return bool(resultado.deleted_count)

        return await self._en_transaccion(operacion)

    async def _exigir_otro_dueno(self, taller_id: str, session: Any) -> None:
        # Dos transacciones podrían degradar dueños distintos y observar el
        # mismo snapshot. Escribir el dueño de menor ID serializa todas las
        # mutaciones que reducen dueños; un write conflict fuerza el reintento
        # de ``with_transaction`` antes de volver a contar.
        bloqueo = await self._coleccion.find_one(
            {"taller_id": taller_id, "rol": RolMembresia.DUENO.value},
            sort=[("_id", ASCENDING)],
            session=session,
        )
        if bloqueo is None:
            raise Conflicto("El Taller no puede quedar sin dueño")
        await self._coleccion.update_one(
            {"_id": bloqueo["_id"], "taller_id": taller_id},
            {"$inc": {"_version_invariante_duenos": 1}},
            session=session,
        )
        cantidad = await self._coleccion.count_documents(
            {"taller_id": taller_id, "rol": RolMembresia.DUENO.value},
            session=session,
        )
        if cantidad <= 1:
            raise Conflicto("El Taller no puede quedar sin dueño")

    async def _en_transaccion(
        self,
        operacion: Callable[[Any], Awaitable[ResultadoTransaccion]],
    ) -> ResultadoTransaccion:
        async with self._cliente.start_session() as session:
            resultado = await session.with_transaction(operacion)
            return cast(ResultadoTransaccion, resultado)

    @staticmethod
    def _a_dominio(documento: dict[str, Any]) -> Membresia:
        return Membresia(
            id=str(documento["_id"]),
            taller_id=documento["taller_id"],
            usuario_id=documento["usuario_id"],
            rol=RolMembresia(documento["rol"]),
        )
