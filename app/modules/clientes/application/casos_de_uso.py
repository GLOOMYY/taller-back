"""Casos de uso del módulo Clientes."""

from app.modules.clientes.application.errores import ClienteNoEncontrado
from app.modules.clientes.application.puertos import (
    PaginaClientes,
    RepositorioClientes,
)
from app.modules.clientes.domain.entidades import CambiosCliente, Cliente
from app.shared.application.contexto import ContextoTaller

LIMITE_PREDETERMINADO = 20
LIMITE_MAXIMO = 100


class ServicioClientes:
    """Coordina operaciones de Clientes bajo un contexto ya autorizado."""

    def __init__(self, repositorio: RepositorioClientes) -> None:
        self._repositorio = repositorio

    async def crear(
        self,
        contexto: ContextoTaller,
        *,
        nombre: str,
        telefono: str | None = None,
        correo: str | None = None,
        notas: str | None = None,
    ) -> Cliente:
        """Crea un Cliente dentro del Taller del contexto."""
        cliente = Cliente.nuevo(
            taller_id=contexto.taller_id,
            nombre=nombre,
            telefono=telefono,
            correo=correo,
            notas=notas,
        )
        return await self._repositorio.crear(contexto, cliente)

    async def listar(
        self,
        contexto: ContextoTaller,
        *,
        limite: int = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
        texto: str | None = None,
    ) -> PaginaClientes:
        """Lista Clientes del Taller autorizado."""
        if limite < 1 or limite > LIMITE_MAXIMO:
            raise ValueError(f"El límite debe estar entre 1 y {LIMITE_MAXIMO}.")
        if texto is None:
            return await self._repositorio.listar(
                contexto, limite=limite, cursor=cursor
            )
        return await self._repositorio.listar(
            contexto, limite=limite, cursor=cursor, texto=texto
        )

    async def obtener(self, contexto: ContextoTaller, cliente_id: str) -> Cliente:
        """Obtiene un Cliente sin revelar registros de otros Talleres."""
        cliente = await self._repositorio.obtener(contexto, cliente_id)
        if cliente is None:
            raise ClienteNoEncontrado()
        return cliente

    async def actualizar(
        self,
        contexto: ContextoTaller,
        cliente_id: str,
        cambios: CambiosCliente,
    ) -> Cliente:
        """Edita un Cliente del Taller autorizado."""
        actual = await self._repositorio.obtener(contexto, cliente_id)
        if actual is None:
            raise ClienteNoEncontrado()
        actualizado = actual.actualizar(cambios)
        resultado = await self._repositorio.actualizar(contexto, actualizado)
        if resultado is None:
            raise ClienteNoEncontrado()
        return resultado
