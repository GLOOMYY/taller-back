"""Composición explícita de casos de uso y adaptadores de fase 1."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any
from uuid import uuid4

from fastapi import Depends, Request
from pymongo import AsyncMongoClient

from app.core.config import Settings
from app.core.mongodb import crear_cliente_mongodb
from app.modules.catalogos.composicion import ModuloCatalogos, componer_catalogos
from app.modules.clientes.application import ServicioClientes
from app.modules.clientes.infrastructure.mongodb import RepositorioClientesMongo
from app.modules.comprobantes.application.servicio import ServicioComprobantes
from app.modules.comprobantes.infrastructure.reportlab import (
    GeneradorComprobanteReportLab,
)
from app.modules.dispositivos.composicion import (
    ModuloDispositivos,
    componer_dispositivos,
)
from app.modules.membresias.application import ServicioMembresias
from app.modules.membresias.infrastructure.mongo import RepositorioMembresiasMongo
from app.modules.operaciones import ServicioOperaciones
from app.modules.referencias.composicion import (
    ModuloReferencias,
    componer_referencias,
)
from app.modules.referencias.datos_iso import catalogos_iso
from app.modules.seguimiento.application.servicio import ServicioSeguimientoPublico
from app.modules.seguimiento.application.tokens import ServicioTokensSeguimiento
from app.modules.talleres.application import ServicioTalleres
from app.modules.talleres.domain.modelos import Taller
from app.modules.talleres.infrastructure.mongo import (
    GeneradorUuid as GeneradorUuidTaller,
)
from app.modules.talleres.infrastructure.mongo import RepositorioTalleresMongo
from app.modules.usuarios.application import ServicioUsuarios
from app.modules.usuarios.domain.modelos import IdentidadOidc
from app.modules.usuarios.infrastructure.mongo import (
    GeneradorUuid as GeneradorUuidUsuario,
)
from app.modules.usuarios.infrastructure.mongo import RepositorioUsuariosMongo
from app.security.dependencias import crear_dependencia_identidad
from app.security.oidc import VerificadorOidcPyJwt
from app.security.servicio import ServicioIdentidad
from app.shared.application import NoAutenticado
from app.shared.application.contexto import ContextoIdentidad, ContextoTaller


class UnidadCreacionTallerMongo:
    """Transacción que crea Taller y Membresía de dueño como una unidad."""

    def __init__(
        self,
        cliente: AsyncMongoClient[Any],
        talleres: RepositorioTalleresMongo,
        membresias: ServicioMembresias,
        metodos_pago: Any,
    ) -> None:
        self._cliente = cliente
        self._talleres = talleres
        self._membresias = membresias
        self._metodos_pago = metodos_pago
        self._session: Any | None = None

    async def __aenter__(self) -> "UnidadCreacionTallerMongo":
        self._session = self._cliente.start_session()
        await self._session.start_transaction()
        return self

    async def __aexit__(
        self,
        tipo_error: type[BaseException] | None,
        error: BaseException | None,
        traza: object | None,
    ) -> bool | None:
        if self._session is None:
            return None
        try:
            if tipo_error is None:
                await self._session.commit_transaction()
            else:
                await self._session.abort_transaction()
        finally:
            await self._session.end_session()
        return None

    async def guardar_taller(self, taller: Taller) -> None:
        if self._session is None:
            raise RuntimeError("La transacción de Taller no está iniciada")
        await self._talleres.crear(taller, session=self._session)

    async def crear_membresia_dueno(self, taller_id: str, usuario_id: str) -> None:
        if self._session is None:
            raise RuntimeError("La transacción de Taller no está iniciada")
        await self._membresias.crear_dueno_inicial(
            taller_id,
            usuario_id,
            session=self._session,
        )

    async def crear_metodo_efectivo(self, taller_id: str) -> None:
        """Inserta el método inicial dentro de la transacción del Taller."""
        if self._session is None:
            raise RuntimeError("La transacción de Taller no está iniciada")
        await self._metodos_pago.insert_one(
            {
                "_id": str(uuid4()),
                "taller_id": taller_id,
                "nombre": "Efectivo",
                "nombre_normalizado": "efectivo",
                "activo": True,
            },
            session=self._session,
        )


@dataclass(slots=True)
class Contenedor:
    """Objetos de larga vida compartidos por el adaptador HTTP."""

    settings: Settings
    cliente_mongodb: AsyncMongoClient[Any]
    usuarios: ServicioUsuarios
    talleres: ServicioTalleres
    membresias: ServicioMembresias
    clientes: ServicioClientes
    referencias: ModuloReferencias
    catalogos: ModuloCatalogos
    dispositivos: ModuloDispositivos
    operaciones: ServicioOperaciones
    seguimiento: ServicioSeguimientoPublico
    comprobantes: ServicioComprobantes
    repositorio_usuarios: RepositorioUsuariosMongo
    repositorio_membresias: RepositorioMembresiasMongo
    repositorio_clientes: RepositorioClientesMongo
    verificar_oidc: VerificadorOidcPyJwt

    async def crear_indices(self) -> None:
        """Materializa las restricciones de persistencia aceptadas."""

        await self.repositorio_usuarios.crear_indices()
        await self.repositorio_membresias.crear_indices()
        await self.repositorio_clientes.crear_indices()
        await self.referencias.repositorio.crear_indices()
        paises, monedas = catalogos_iso()
        await self.referencias.repositorio.sincronizar_catalogos(paises, monedas)
        await self.catalogos.repositorio.crear_indices()
        await self.dispositivos.repositorio.crear_indices()
        await self.operaciones.crear_indices()


def crear_contenedor(
    settings: Settings,
    cliente_mongodb: AsyncMongoClient[Any] | None = None,
) -> Contenedor:
    """Conecta módulos únicamente mediante sus contratos públicos."""

    cliente = cliente_mongodb or crear_cliente_mongodb(settings)
    base_datos = cliente[settings.mongodb_database]
    repositorio_usuarios = RepositorioUsuariosMongo(base_datos["usuarios"])
    servicio_usuarios = ServicioUsuarios(
        repositorio_usuarios,
        GeneradorUuidUsuario(),
    )
    repositorio_membresias = RepositorioMembresiasMongo(
        base_datos["membresias"], cliente
    )
    servicio_membresias = ServicioMembresias(
        repositorio_membresias,
        servicio_usuarios,
        lambda: str(uuid4()),
    )
    repositorio_talleres = RepositorioTalleresMongo(
        base_datos["talleres"],
        base_datos["referencias_paises"],
        base_datos["referencias_monedas"],
    )

    def crear_unidad() -> UnidadCreacionTallerMongo:
        return UnidadCreacionTallerMongo(
            cliente,
            repositorio_talleres,
            servicio_membresias,
            base_datos["metodos_pago"],
        )

    servicio_talleres = ServicioTalleres(
        repositorio_talleres,
        servicio_membresias,
        crear_unidad,
        GeneradorUuidTaller(),
    )
    repositorio_clientes = RepositorioClientesMongo(base_datos)
    servicio_clientes = ServicioClientes(repositorio_clientes)
    modulo_referencias = componer_referencias(base_datos)
    modulo_catalogos = componer_catalogos(base_datos)
    modulo_dispositivos = componer_dispositivos(
        base_datos,
        obtener_cliente=servicio_clientes.obtener,
        obtener_modelo_seleccionable=(
            modulo_catalogos.servicio.obtener_modelo_seleccionable
        ),
    )
    servicio_operaciones = ServicioOperaciones(base_datos, cliente)
    tokens_seguimiento = ServicioTokensSeguimiento(
        settings.seguimiento_hmac_secreto.get_secret_value()
    )
    servicio_seguimiento = ServicioSeguimientoPublico(base_datos, tokens_seguimiento)
    servicio_comprobantes = ServicioComprobantes(GeneradorComprobanteReportLab())
    verificador = VerificadorOidcPyJwt(
        issuer=str(settings.oidc_issuer),
        audience=settings.oidc_audience,
        jwks_url=settings.jwks_url,
    )
    return Contenedor(
        settings=settings,
        cliente_mongodb=cliente,
        usuarios=servicio_usuarios,
        talleres=servicio_talleres,
        membresias=servicio_membresias,
        clientes=servicio_clientes,
        referencias=modulo_referencias,
        catalogos=modulo_catalogos,
        dispositivos=modulo_dispositivos,
        operaciones=servicio_operaciones,
        seguimiento=servicio_seguimiento,
        comprobantes=servicio_comprobantes,
        repositorio_usuarios=repositorio_usuarios,
        repositorio_membresias=repositorio_membresias,
        repositorio_clientes=repositorio_clientes,
        verificar_oidc=verificador,
    )


def crear_dependencias(
    contenedor: Contenedor,
) -> tuple[
    Callable[..., Any],
    Callable[..., Any],
    Callable[..., Any],
    Callable[..., Any],
]:
    """Crea dependencias OIDC, Usuario, tenant y Clientes para routers."""

    async def obtener_oidc(request: Request) -> IdentidadOidc:
        autorizacion = request.headers.get("Authorization", "")
        esquema, separador, token = autorizacion.partition(" ")
        if not separador or esquema.lower() != "bearer" or not token.strip():
            raise NoAutenticado("Token ausente o inválido")
        identidad = await contenedor.verificar_oidc.verificar(token.strip())
        return IdentidadOidc(
            issuer=identidad.issuer,
            subject=identidad.subject,
        )

    servicio_identidad = ServicioIdentidad(
        contenedor.verificar_oidc,
        contenedor.usuarios,
    )
    obtener_identidad = crear_dependencia_identidad(servicio_identidad)

    async def obtener_contexto(
        taller_id: str,
        identidad: Annotated[ContextoIdentidad, Depends(obtener_identidad)],
    ) -> ContextoTaller:
        return await contenedor.membresias.resolver_contexto_taller(
            identidad,
            taller_id,
        )

    def obtener_servicio_clientes() -> ServicioClientes:
        return contenedor.clientes

    return (
        obtener_oidc,
        obtener_identidad,
        obtener_contexto,
        obtener_servicio_clientes,
    )
