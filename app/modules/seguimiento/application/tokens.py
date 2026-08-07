"""Tokens permanentes HMAC para enlaces publicos de seguimiento."""

import base64
import binascii
import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Final

_PREFIJO: Final = "st1"
_CONTEXTO_FIRMA: Final = b"taller-app:seguimiento-publico:v1:"
_LONGITUD_FIRMA: Final = hashlib.sha256().digest_size


class TokenSeguimientoInvalido(ValueError):
    """El token no tiene una firma o estructura valida."""

    def __init__(self) -> None:
        super().__init__("El token de seguimiento no es valido.")


@dataclass(frozen=True, slots=True)
class ReferenciaSeguimiento:
    """Referencia autenticada extraida de un token publico."""

    orden_id: str
    version: int


class ServicioTokensSeguimiento:
    """Emite y verifica referencias firmadas sin almacenar los tokens.

    Los tokens no caducan. La capa que carga la Orden debe comparar ``version``
    con su version publica vigente; incrementarla rota o revoca enlaces previos.
    """

    def __init__(self, secreto: str | bytes) -> None:
        secreto_bytes = secreto.encode("utf-8") if isinstance(secreto, str) else secreto
        if len(secreto_bytes) < 32:
            raise ValueError("El secreto HMAC debe contener al menos 32 bytes.")
        self._secreto = secreto_bytes

    def emitir(self, *, orden_id: str, version: int) -> str:
        """Firma la identidad y version publica actual de una Orden."""
        referencia = self._validar_referencia(orden_id=orden_id, version=version)
        payload = json.dumps(
            {"orden_id": referencia.orden_id, "version": referencia.version},
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        payload_codificado = self._codificar(payload)
        mensaje = self._mensaje_firmado(payload_codificado)
        firma = hmac.new(self._secreto, mensaje, hashlib.sha256).digest()
        return f"{_PREFIJO}.{payload_codificado}.{self._codificar(firma)}"

    def verificar(self, token: str) -> ReferenciaSeguimiento:
        """Verifica autenticidad y devuelve los datos que deben consultarse."""
        try:
            prefijo, payload_codificado, firma_codificada = token.split(".")
            if prefijo != _PREFIJO or not payload_codificado or not firma_codificada:
                raise TokenSeguimientoInvalido()
            firma = self._decodificar(firma_codificada)
            if len(firma) != _LONGITUD_FIRMA:
                raise TokenSeguimientoInvalido()
            esperada = hmac.new(
                self._secreto,
                self._mensaje_firmado(payload_codificado),
                hashlib.sha256,
            ).digest()
            if not hmac.compare_digest(firma, esperada):
                raise TokenSeguimientoInvalido()
            payload = json.loads(self._decodificar(payload_codificado).decode("utf-8"))
            if not isinstance(payload, dict) or set(payload) != {"orden_id", "version"}:
                raise TokenSeguimientoInvalido()
            orden_id = payload["orden_id"]
            version = payload["version"]
            if not isinstance(orden_id, str) or isinstance(version, bool):
                raise TokenSeguimientoInvalido()
            if not isinstance(version, int):
                raise TokenSeguimientoInvalido()
            return self._validar_referencia(orden_id=orden_id, version=version)
        except TokenSeguimientoInvalido:
            raise
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError, binascii.Error):
            raise TokenSeguimientoInvalido() from None

    @staticmethod
    def version_vigente(
        referencia: ReferenciaSeguimiento, *, version_actual: int
    ) -> bool:
        """Permite aplicar revocacion/rotacion sin conservar el token emitido."""
        return hmac.compare_digest(str(referencia.version), str(version_actual))

    @staticmethod
    def _validar_referencia(*, orden_id: str, version: int) -> ReferenciaSeguimiento:
        if not orden_id or orden_id != orden_id.strip() or len(orden_id) > 200:
            raise ValueError("La Orden requiere un identificador valido.")
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise ValueError("La version de seguimiento debe ser un entero positivo.")
        return ReferenciaSeguimiento(orden_id=orden_id, version=version)

    @staticmethod
    def _mensaje_firmado(payload_codificado: str) -> bytes:
        return _CONTEXTO_FIRMA + payload_codificado.encode("ascii")

    @staticmethod
    def _codificar(valor: bytes) -> str:
        return base64.urlsafe_b64encode(valor).rstrip(b"=").decode("ascii")

    @staticmethod
    def _decodificar(valor: str) -> bytes:
        relleno = "=" * (-len(valor) % 4)
        return base64.b64decode(valor + relleno, altchars=b"-_", validate=True)
