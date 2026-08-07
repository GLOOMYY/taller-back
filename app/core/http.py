"""Middleware y traducción segura de errores HTTP."""

import logging
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from app.shared.application.errores import (
    Conflicto,
    ErrorAplicacion,
    NoAutenticado,
    NoEncontrado,
    Prohibido,
)

logger = logging.getLogger("taller.api")


class DetalleErrorSalida(BaseModel):
    """Detalle seguro de un campo inválido."""

    campo: str
    mensaje: str
    tipo: str


class ErrorSalida(BaseModel):
    """Contrato uniforme de errores de la API."""

    codigo: str
    mensaje: str
    correlacion_id: str
    detalles: list[DetalleErrorSalida] | None = None


ESTADOS_ERROR: dict[type[ErrorAplicacion], int] = {
    NoAutenticado: 401,
    Prohibido: 403,
    NoEncontrado: 404,
    Conflicto: 409,
}


def configurar_http(application: FastAPI) -> None:
    """Instala correlación y handlers sin divulgar payloads o credenciales."""

    @application.middleware("http")
    async def correlacion(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        correlacion_id = request.headers.get("X-Correlation-ID") or str(uuid4())
        request.state.correlacion_id = correlacion_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlacion_id
        return response

    @application.exception_handler(ErrorAplicacion)
    async def error_aplicacion(
        request: Request,
        error: ErrorAplicacion,
    ) -> JSONResponse:
        status = next(
            (
                value
                for error_type, value in ESTADOS_ERROR.items()
                if isinstance(error, error_type)
            ),
            400,
        )
        return JSONResponse(
            status_code=status,
            content={
                "codigo": error.codigo,
                "mensaje": error.mensaje,
                "correlacion_id": request.state.correlacion_id,
            },
        )

    @application.exception_handler(RequestValidationError)
    async def entrada_invalida(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        detalles = [
            {
                "campo": ".".join(str(parte) for parte in item["loc"]),
                "mensaje": item["msg"],
                "tipo": item["type"],
            }
            for item in error.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "codigo": "entrada_invalida",
                "mensaje": "La entrada no es válida.",
                "correlacion_id": request.state.correlacion_id,
                "detalles": detalles,
            },
        )

    @application.exception_handler(ValueError)
    async def valor_invalido(request: Request, error: ValueError) -> JSONResponse:
        """Traduce invariantes de entrada del dominio sin devolver una traza."""
        return JSONResponse(
            status_code=422,
            content={
                "codigo": "entrada_invalida",
                "mensaje": str(error) or "La entrada no es válida.",
                "correlacion_id": request.state.correlacion_id,
            },
        )

    @application.exception_handler(HTTPException)
    async def error_http(request: Request, error: HTTPException) -> JSONResponse:
        codigos = {
            401: "no_autenticado",
            403: "prohibido",
            404: "no_encontrado",
            409: "conflicto",
            422: "entrada_invalida",
            503: "no_disponible",
        }
        mensaje = (
            error.detail if isinstance(error.detail, str) else "Solicitud inválida."
        )
        return JSONResponse(
            status_code=error.status_code,
            headers=error.headers,
            content={
                "codigo": codigos.get(error.status_code, "error_http"),
                "mensaje": mensaje,
                "correlacion_id": request.state.correlacion_id,
            },
        )

    @application.exception_handler(Exception)
    async def error_interno(request: Request, error: Exception) -> JSONResponse:
        logger.exception(
            "error_interno correlacion_id=%s tipo=%s",
            request.state.correlacion_id,
            type(error).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={
                "codigo": "error_interno",
                "mensaje": "Ocurrió un error interno.",
                "correlacion_id": request.state.correlacion_id,
            },
        )
