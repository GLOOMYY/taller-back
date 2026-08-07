"""Errores esperados de los casos de uso de Clientes."""

from app.shared.application.errores import NoEncontrado


class ClienteNoEncontrado(NoEncontrado):
    """Indica que un Cliente no es accesible en el Taller autorizado."""


class CursorClientesInvalido(ValueError):
    """Indica que el cursor de Clientes no tiene un formato válido."""
