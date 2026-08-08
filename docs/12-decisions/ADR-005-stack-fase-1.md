# ADR-005: Stack y contrato técnico de fase 1

- **Estado:** Aceptado
- **Fecha:** 2026-08-07

## Decisión

FastAPI será el adaptador HTTP asíncrono bajo `/api/v1`. La API gestionará
cuentas locales y validará tokens JWT HS256 con PyJWT contra el emisor
configurado. La identidad interna se resuelve mediante la clave única
`issuer + sub`; las contraseñas solo se almacenan como hash.

La API usa recursos y campos en español, OpenAPI generado por FastAPI y errores
seguros con `codigo`, `mensaje` y `correlacion_id`. Los listados usan cursor
opaco con orden estable por identificador, límite 20 por defecto y máximo 100.
Los IDs externos son strings opacos.

## Consecuencias

Los secretos y URLs se reciben por variables de entorno. La verificación exige
firma, expiración e issuer correctos. FastAPI, PyJWT o MongoDB no se importan
desde Domain. Producción, MFA y recuperación quedan fuera de fase 1.
