"""Valores globales de países y monedas ISO."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Pais:
    """País identificado por un código ISO 3166-1 alfa-2."""

    codigo: str
    nombre: str

    def __post_init__(self) -> None:
        codigo = self.codigo.strip().upper()
        nombre = self.nombre.strip()
        if len(codigo) != 2 or not codigo.isalpha() or not codigo.isascii():
            raise ValueError("El código de país ISO debe tener dos letras ASCII.")
        if not nombre:
            raise ValueError("El nombre del país es obligatorio.")
        object.__setattr__(self, "codigo", codigo)
        object.__setattr__(self, "nombre", nombre)


@dataclass(frozen=True, slots=True)
class Moneda:
    """Moneda identificada por ISO 4217 y su precisión monetaria."""

    codigo: str
    nombre: str
    simbolo: str
    decimales: int

    def __post_init__(self) -> None:
        codigo = self.codigo.strip().upper()
        nombre = self.nombre.strip()
        simbolo = self.simbolo.strip()
        if len(codigo) != 3 or not codigo.isalpha() or not codigo.isascii():
            raise ValueError("El código de moneda ISO debe tener tres letras ASCII.")
        if not nombre or not simbolo:
            raise ValueError("El nombre y símbolo de la moneda son obligatorios.")
        if self.decimales < 0 or self.decimales > 4:
            raise ValueError("La precisión ISO de la moneda no es válida.")
        object.__setattr__(self, "codigo", codigo)
        object.__setattr__(self, "nombre", nombre)
        object.__setattr__(self, "simbolo", simbolo)
