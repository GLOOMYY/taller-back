"""Router FastAPI del módulo Clientes."""

from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.modules.clientes.application.casos_de_uso import (
    LIMITE_MAXIMO,
    LIMITE_PREDETERMINADO,
    ServicioClientes,
)
from app.modules.clientes.application.errores import CursorClientesInvalido
from app.modules.clientes.domain.entidades import CambiosCliente, Cliente
from app.modules.clientes.domain.errores import ClienteInvalido
from app.shared.application.contexto import ContextoTaller


class ClienteCrearEntrada(BaseModel):
    """Entrada pública para registrar un Cliente."""

    model_config = ConfigDict(extra="forbid")

    nombre: str
    telefono: str | None = None
    correo: str | None = None
    notas: str | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        """Rechaza nombres vacíos sin imponer reglas no aprobadas."""
        if not valor.strip():
            raise ValueError("El nombre es obligatorio.")
        return valor.strip()


class ClienteEditarEntrada(BaseModel):
    """Entrada pública para editar campos presentes."""

    model_config = ConfigDict(extra="forbid")

    nombre: str | None = None
    telefono: str | None = None
    correo: str | None = None
    notas: str | None = None

    @model_validator(mode="after")
    def validar_campos(self) -> "ClienteEditarEntrada":
        """Exige al menos un campo y un nombre no vacío cuando está presente."""
        if not self.model_fields_set:
            raise ValueError("Debe indicarse al menos un campo para editar.")
        if "nombre" in self.model_fields_set:
            if self.nombre is None or not self.nombre.strip():
                raise ValueError("El nombre es obligatorio.")
            self.nombre = self.nombre.strip()
        return self

    def a_cambios(self) -> CambiosCliente:
        """Convierte presencia Pydantic a semántica de patch del dominio."""
        presentes = self.model_fields_set
        return CambiosCliente(
            nombre_definido="nombre" in presentes,
            nombre=self.nombre,
            telefono_definido="telefono" in presentes,
            telefono=self.telefono,
            correo_definido="correo" in presentes,
            correo=self.correo,
            notas_definidas="notas" in presentes,
            notas=self.notas,
        )


class ClienteSalida(BaseModel):
    """Representación pública sin detalles de MongoDB."""

    id: str
    nombre: str
    telefono: str | None
    correo: str | None
    notas: str | None

    @classmethod
    def desde_entidad(cls, cliente: Cliente) -> "ClienteSalida":
        """Traduce una entidad persistida a respuesta HTTP."""
        if cliente.id is None:
            raise RuntimeError("No se puede presentar un Cliente sin id.")
        return cls(
            id=cliente.id,
            nombre=cliente.nombre,
            telefono=cliente.telefono,
            correo=cliente.correo,
            notas=cliente.notas,
        )


class PaginaClientesSalida(BaseModel):
    """Respuesta paginada de Clientes."""

    items: list[ClienteSalida]
    siguiente_cursor: str | None


def crear_router(
    obtener_servicio: Callable[..., ServicioClientes],
    obtener_contexto: Callable[..., ContextoTaller],
) -> APIRouter:
    """Construye el router con dependencias provistas por la composición."""
    router = APIRouter(prefix="/talleres/{taller_id}/clientes", tags=["clientes"])

    @router.post("", response_model=ClienteSalida, status_code=status.HTTP_201_CREATED)
    async def crear_cliente(
        entrada: ClienteCrearEntrada,
        servicio: Annotated[ServicioClientes, Depends(obtener_servicio)],
        contexto: Annotated[ContextoTaller, Depends(obtener_contexto)],
    ) -> ClienteSalida:
        try:
            cliente = await servicio.crear(contexto, **entrada.model_dump())
        except ClienteInvalido as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return ClienteSalida.desde_entidad(cliente)

    @router.get("", response_model=PaginaClientesSalida)
    async def listar_clientes(
        servicio: Annotated[ServicioClientes, Depends(obtener_servicio)],
        contexto: Annotated[ContextoTaller, Depends(obtener_contexto)],
        limite: Annotated[int, Query(ge=1, le=LIMITE_MAXIMO)] = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
        texto: str | None = None,
    ) -> PaginaClientesSalida:
        try:
            pagina = await servicio.listar(
                contexto, limite=limite, cursor=cursor, texto=texto
            )
        except CursorClientesInvalido as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return PaginaClientesSalida(
            items=[ClienteSalida.desde_entidad(item) for item in pagina.items],
            siguiente_cursor=pagina.siguiente_cursor,
        )

    @router.get("/{cliente_id}", response_model=ClienteSalida)
    async def obtener_cliente(
        cliente_id: str,
        servicio: Annotated[ServicioClientes, Depends(obtener_servicio)],
        contexto: Annotated[ContextoTaller, Depends(obtener_contexto)],
    ) -> ClienteSalida:
        cliente = await servicio.obtener(contexto, cliente_id)
        return ClienteSalida.desde_entidad(cliente)

    @router.patch("/{cliente_id}", response_model=ClienteSalida)
    async def actualizar_cliente(
        cliente_id: str,
        entrada: ClienteEditarEntrada,
        servicio: Annotated[ServicioClientes, Depends(obtener_servicio)],
        contexto: Annotated[ContextoTaller, Depends(obtener_contexto)],
    ) -> ClienteSalida:
        try:
            cliente = await servicio.actualizar(
                contexto, cliente_id, entrada.a_cambios()
            )
        except ClienteInvalido as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return ClienteSalida.desde_entidad(cliente)

    return router
