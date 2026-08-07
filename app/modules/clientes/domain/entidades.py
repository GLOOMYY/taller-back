"""Entidades del dominio de Clientes, independientes de persistencia."""

from dataclasses import dataclass, replace

from app.modules.clientes.domain.errores import ClienteInvalido


@dataclass(frozen=True, slots=True)
class CambiosCliente:
    """Campos presentes en una edición parcial de Cliente."""

    nombre_definido: bool = False
    nombre: str | None = None
    telefono_definido: bool = False
    telefono: str | None = None
    correo_definido: bool = False
    correo: str | None = None
    notas_definidas: bool = False
    notas: str | None = None

    @property
    def esta_vacio(self) -> bool:
        """Indica si la solicitud no contiene ningún campo editable."""
        return not any(
            (
                self.nombre_definido,
                self.telefono_definido,
                self.correo_definido,
                self.notas_definidas,
            )
        )


@dataclass(frozen=True, slots=True)
class Cliente:
    """Cliente que existe exclusivamente dentro de un Taller."""

    id: str | None
    taller_id: str
    nombre: str
    telefono: str | None = None
    correo: str | None = None
    notas: str | None = None

    def __post_init__(self) -> None:
        nombre_limpio = self.nombre.strip()
        if not nombre_limpio:
            raise ClienteInvalido("El nombre del Cliente es obligatorio.")
        if not self.taller_id:
            raise ClienteInvalido("El Cliente requiere contexto de Taller.")
        object.__setattr__(self, "nombre", nombre_limpio)

    @classmethod
    def nuevo(
        cls,
        *,
        taller_id: str,
        nombre: str,
        telefono: str | None = None,
        correo: str | None = None,
        notas: str | None = None,
    ) -> "Cliente":
        """Construye un Cliente aún no persistido."""
        return cls(
            id=None,
            taller_id=taller_id,
            nombre=nombre,
            telefono=telefono,
            correo=correo,
            notas=notas,
        )

    def actualizar(self, cambios: CambiosCliente) -> "Cliente":
        """Aplica una edición parcial preservando invariantes."""
        if cambios.esta_vacio:
            raise ClienteInvalido("Debe indicarse al menos un campo para editar.")
        nuevo_nombre = self.nombre
        if cambios.nombre_definido:
            if cambios.nombre is None:
                raise ClienteInvalido("El nombre del Cliente no puede ser nulo.")
            nuevo_nombre = cambios.nombre
        return replace(
            self,
            nombre=nuevo_nombre,
            telefono=(cambios.telefono if cambios.telefono_definido else self.telefono),
            correo=cambios.correo if cambios.correo_definido else self.correo,
            notas=cambios.notas if cambios.notas_definidas else self.notas,
        )
