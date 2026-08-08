# Autenticación

## Decisión aceptada para fase 1

La API administra cuentas locales y emite tokens JWT firmados con HS256. Las
contraseñas se almacenan únicamente como hashes `scrypt`; nunca se persisten en
claro. El secreto, emisor y expiración se inyectan por entorno mediante
`TALLER_JWT_SECRETO`, `TALLER_JWT_EMISOR` y `TALLER_JWT_EXPIRACION_MINUTOS`.

## Flujo

1. Presentation extrae un esquema `Bearer` del header `Authorization`.
2. El adaptador verifica firma HS256, `issuer`, `exp`, `iat`, `iss`, `sub` y
   el tipo de token.
3. El `sub` verificado se resuelve mediante el contrato público de Usuarios.
4. Solo un Usuario interno existente produce `ContextoIdentidad`.
5. Para una ruta tenant-scoped, Membresías deriva después `ContextoTaller`.

`PyJWKClient` es síncrono, por lo que descarga/verificación se ejecuta fuera del
event loop. Las pruebas inyectan dobles de JWKS/decoder y nunca acceden a red.

## Denegaciones

Token ausente, esquema incorrecto, firma inválida, token expirado, emisor
incorrecto, claims obligatorios ausentes e identidad sin Usuario
interno producen `401` con mensaje seguro. No se registran tokens, claims
completos, payloads ni datos personales.

El mapeo de `sub` implementa BR-021 y la política HTTP implementa AC-023.

MFA, recuperación de cuenta y refresh tokens quedan fuera del backend fase 1.
