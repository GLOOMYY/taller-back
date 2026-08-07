"""Casos de uso de Membresías y autorización por Taller."""

from collections.abc import Callable

from app.modules.membresias.application.puertos import (
    DirectorioUsuarios,
    RepositorioMembresias,
)
from app.modules.membresias.domain.modelos import Membresia, RolMembresia
from app.shared.application import Conflicto, NoEncontrado, Prohibido
from app.shared.application.contexto import ContextoIdentidad, ContextoTaller


class ServicioMembresias:
    """Administra Membresías y deriva contexto tenant autorizado."""

    def __init__(
        self,
        repositorio: RepositorioMembresias,
        usuarios: DirectorioUsuarios,
        generar_id: Callable[[], str],
    ) -> None:
        self._repositorio = repositorio
        self._usuarios = usuarios
        self._generar_id = generar_id

    async def resolver_contexto_taller(
        self, identidad: ContextoIdentidad, taller_id: str
    ) -> ContextoTaller:
        """Deriva el Taller autorizado sin confiar solo en el path."""
        membresia = await self._repositorio.obtener(taller_id, identidad.usuario_id)
        if membresia is None:
            raise NoEncontrado("Taller no encontrado")
        return ContextoTaller(
            usuario_id=identidad.usuario_id,
            taller_id=taller_id,
            rol=membresia.rol.value,
        )

    async def listar(
        self,
        contexto: ContextoTaller,
        limite: int = 20,
        despues_de: str | None = None,
    ) -> list[Membresia]:
        """Lista miembros para un contexto previamente autorizado."""
        self._exigir_dueno(contexto)
        if not 1 <= limite <= 101:
            raise ValueError("limite debe estar entre 1 y 101")
        return await self._repositorio.listar(contexto.taller_id, limite, despues_de)

    async def listar_taller_ids(self, usuario_id: str) -> list[str]:
        """Expone solo IDs accesibles al módulo Talleres."""
        return await self._repositorio.listar_taller_ids(usuario_id)

    async def obtener_rol_actual(self, usuario_id: str, taller_id: str) -> str | None:
        """Expone el rol mínimo requerido por el selector de Taller."""
        membresia = await self._repositorio.obtener(taller_id, usuario_id)
        return membresia.rol.value if membresia is not None else None

    async def crear_dueno_inicial(
        self,
        taller_id: str,
        usuario_id: str,
        *,
        session: object | None = None,
    ) -> Membresia:
        """Participa en la transacción de creación de un Taller.

        Este contrato público solo debe invocarlo el caso de uso que crea el
        Taller; no se expone como operación HTTP independiente.
        """
        membresia = Membresia(
            id=self._generar_id(),
            taller_id=taller_id,
            usuario_id=usuario_id,
            rol=RolMembresia.DUENO,
        )
        await self._repositorio.crear(membresia, session=session)
        return membresia

    async def agregar(
        self,
        contexto: ContextoTaller,
        nombre_usuario: str,
        rol: RolMembresia,
    ) -> Membresia:
        """Agrega por arroba a un Usuario ya registrado."""
        self._exigir_dueno(contexto)
        usuario = await self._usuarios.buscar_por_nombre_usuario(nombre_usuario)
        if usuario is None:
            raise NoEncontrado("Usuario no encontrado")
        existente = await self._repositorio.obtener(contexto.taller_id, usuario.id)
        if existente is not None:
            raise Conflicto("El Usuario ya es miembro del Taller")
        membresia = Membresia(
            id=self._generar_id(),
            taller_id=contexto.taller_id,
            usuario_id=usuario.id,
            rol=rol,
        )
        await self._repositorio.crear(membresia)
        return membresia

    async def cambiar_rol(
        self,
        contexto: ContextoTaller,
        usuario_id: str,
        rol: RolMembresia,
    ) -> Membresia:
        """Cambia el rol preservando al menos un dueño."""
        self._exigir_dueno(contexto)
        membresia = await self._repositorio.cambiar_rol_protegiendo_ultimo_dueno(
            contexto.taller_id, usuario_id, rol
        )
        if membresia is None:
            raise NoEncontrado("Miembro no encontrado")
        return membresia

    async def retirar(self, contexto: ContextoTaller, usuario_id: str) -> None:
        """Retira un miembro preservando al menos un dueño."""
        self._exigir_dueno(contexto)
        retirado = await self._repositorio.retirar_protegiendo_ultimo_dueno(
            contexto.taller_id, usuario_id
        )
        if not retirado:
            raise NoEncontrado("Miembro no encontrado")

    @staticmethod
    def _exigir_dueno(contexto: ContextoTaller) -> None:
        if contexto.rol != RolMembresia.DUENO.value:
            raise Prohibido("Solo los dueños administran Membresías")
