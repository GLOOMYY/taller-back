"""Casos de uso tenant-aware de Dispositivos."""

from app.modules.dispositivos.application.puertos import (
    BuscadorReferencia,
    PaginaDispositivos,
    RepositorioDispositivos,
)
from app.modules.dispositivos.domain import CambiosDispositivo, Dispositivo
from app.shared.application.contexto import ContextoTaller
from app.shared.application.errores import NoEncontrado

LIMITE_PREDETERMINADO = 20
LIMITE_MAXIMO = 100


class DispositivoNoEncontrado(NoEncontrado):
    """El equipo no existe dentro del Taller autorizado."""


class ServicioDispositivos:
    """Coordina equipos mediante contratos públicos de Cliente y Modelo."""

    def __init__(
        self,
        repositorio: RepositorioDispositivos,
        obtener_cliente: BuscadorReferencia,
        obtener_modelo_seleccionable: BuscadorReferencia,
    ) -> None:
        self._repositorio = repositorio
        self._obtener_cliente = obtener_cliente
        self._obtener_modelo = obtener_modelo_seleccionable

    async def crear(
        self,
        contexto: ContextoTaller,
        cliente_id: str,
        *,
        modelo_id: str,
        identificador: str | None = None,
        notas: str | None = None,
    ) -> Dispositivo:
        await self._obtener_cliente(contexto, cliente_id)
        await self._obtener_modelo(contexto, modelo_id)
        dispositivo = Dispositivo.nuevo(
            contexto.taller_id,
            cliente_id,
            modelo_id,
            identificador,
            notas,
        )
        return await self._repositorio.crear(contexto, dispositivo)

    async def listar_por_cliente(
        self,
        contexto: ContextoTaller,
        cliente_id: str,
        *,
        limite: int = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
    ) -> PaginaDispositivos:
        if limite < 1 or limite > LIMITE_MAXIMO:
            raise ValueError("El límite debe estar entre 1 y 100.")
        await self._obtener_cliente(contexto, cliente_id)
        return await self._repositorio.listar_por_cliente(
            contexto, cliente_id, limite=limite, cursor=cursor
        )

    async def obtener(
        self, contexto: ContextoTaller, dispositivo_id: str
    ) -> Dispositivo:
        dispositivo = await self._repositorio.obtener(contexto, dispositivo_id)
        if dispositivo is None:
            raise DispositivoNoEncontrado()
        return dispositivo

    async def actualizar(
        self,
        contexto: ContextoTaller,
        dispositivo_id: str,
        cambios: CambiosDispositivo,
    ) -> Dispositivo:
        actual = await self.obtener(contexto, dispositivo_id)
        if cambios.modelo_definido:
            if cambios.modelo_id is None:
                raise ValueError("El modelo es obligatorio.")
            await self._obtener_modelo(contexto, cambios.modelo_id)
        actualizado = actual.actualizar(cambios)
        resultado = await self._repositorio.actualizar(contexto, actualizado)
        if resultado is None:
            raise DispositivoNoEncontrado()
        return resultado
