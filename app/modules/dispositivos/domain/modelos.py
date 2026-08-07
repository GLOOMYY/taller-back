"""Entidad Dispositivo independiente de transporte y persistencia."""

from dataclasses import dataclass, replace


def _opcional(valor: str | None) -> str | None:
    if valor is None:
        return None
    limpio = valor.strip()
    return limpio or None


@dataclass(frozen=True, slots=True)
class CambiosDispositivo:
    """Campos mutables del equipo; Cliente se excluye deliberadamente."""

    modelo_definido: bool = False
    modelo_id: str | None = None
    identificador_definido: bool = False
    identificador: str | None = None
    notas_definidas: bool = False
    notas: str | None = None


@dataclass(frozen=True, slots=True)
class Dispositivo:
    """Equipo de un Cliente dentro de un único Taller."""

    id: str | None
    taller_id: str
    cliente_id: str
    modelo_id: str
    identificador: str | None = None
    notas: str | None = None

    @classmethod
    def nuevo(
        cls,
        taller_id: str,
        cliente_id: str,
        modelo_id: str,
        identificador: str | None = None,
        notas: str | None = None,
    ) -> "Dispositivo":
        if not taller_id.strip() or not cliente_id.strip() or not modelo_id.strip():
            raise ValueError("Taller, Cliente y modelo son obligatorios.")
        return cls(
            None,
            taller_id,
            cliente_id,
            modelo_id,
            _opcional(identificador),
            _opcional(notas),
        )

    def actualizar(self, cambios: CambiosDispositivo) -> "Dispositivo":
        modelo_id = self.modelo_id
        identificador = self.identificador
        notas = self.notas
        if cambios.modelo_definido:
            if cambios.modelo_id is None or not cambios.modelo_id.strip():
                raise ValueError("El modelo es obligatorio.")
            modelo_id = cambios.modelo_id
        if cambios.identificador_definido:
            identificador = _opcional(cambios.identificador)
        if cambios.notas_definidas:
            notas = _opcional(cambios.notas)
        return replace(
            self, modelo_id=modelo_id, identificador=identificador, notas=notas
        )
