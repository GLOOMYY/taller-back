"""Errores estables independientes del transporte HTTP."""


class ErrorAplicacion(Exception):
    """Fallo esperado que Presentation puede traducir de forma segura."""

    codigo = "error_aplicacion"
    mensaje = "No fue posible completar la operación."

    def __init__(self, mensaje: str | None = None) -> None:
        self.mensaje = mensaje or type(self).mensaje
        super().__init__(self.mensaje)


class NoAutenticado(ErrorAplicacion):
    codigo = "no_autenticado"
    mensaje = "Se requiere una identidad válida."


class Prohibido(ErrorAplicacion):
    codigo = "prohibido"
    mensaje = "No tiene permiso para realizar esta operación."


class NoEncontrado(ErrorAplicacion):
    codigo = "no_encontrado"
    mensaje = "El recurso no está disponible."


class Conflicto(ErrorAplicacion):
    codigo = "conflicto"
    mensaje = "La operación entra en conflicto con el estado actual."
