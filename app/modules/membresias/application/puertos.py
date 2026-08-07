"""Puertos requeridos por los casos de uso de Membresías."""

from typing import Protocol

from app.modules.membresias.domain.modelos import Membresia, RolMembresia


class UsuarioReferencia(Protocol):
    """Vista mínima de Usuario consumida mediante su contrato público."""

    @property
    def id(self) -> str:
        """Identificador interno opaco."""

    @property
    def nombre_usuario(self) -> str:
        """Identificador público global y normalizado."""


class DirectorioUsuarios(Protocol):
    """Contrato consumidor para resolver Usuarios existentes por su arroba."""

    async def buscar_por_nombre_usuario(
        self, nombre_usuario: str
    ) -> UsuarioReferencia | None:
        """Devuelve la referencia pública del Usuario, si existe."""


class RepositorioMembresias(Protocol):
    """Persistencia requerida por Membresías.

    Las mutaciones protegidas deben comprobar la regla del último dueño dentro
    de la misma transacción que modifica o elimina la Membresía.
    """

    async def obtener(self, taller_id: str, usuario_id: str) -> Membresia | None:
        """Obtiene un vínculo usando siempre ambos lados del contexto."""

    async def listar(
        self, taller_id: str, limite: int, despues_de: str | None
    ) -> list[Membresia]:
        """Lista los miembros de un Taller en orden determinista."""

    async def listar_taller_ids(self, usuario_id: str) -> list[str]:
        """Lista Talleres accesibles para el contrato público de Talleres."""

    async def crear(self, membresia: Membresia, session: object | None = None) -> None:
        """Crea una Membresía o levanta Conflicto si ya existe."""

    async def cambiar_rol_protegiendo_ultimo_dueno(
        self,
        taller_id: str,
        usuario_id: str,
        rol: RolMembresia,
    ) -> Membresia | None:
        """Cambia el rol atómicamente o levanta Conflicto por último dueño."""

    async def retirar_protegiendo_ultimo_dueno(
        self, taller_id: str, usuario_id: str
    ) -> bool:
        """Retira atómicamente o levanta Conflicto por último dueño."""
