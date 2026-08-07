# Autenticación

## Decisión aceptada para fase 1

Auth0 es el proveedor administrado OIDC. La API recibe access tokens JWT y no
almacena contraseñas, sesiones ni secretos del Usuario. La configuración por
entorno declara el issuer HTTPS del tenant, la audiencia de la API y la URL
JWKS; ningún valor sensible se embebe en código o fixtures.
El issuer se conserva exactamente como lo publica OIDC (incluido el `/` final
de Auth0) y debe coincidir literalmente durante verificación y mapeo interno.

La verificación usa `PyJWT[crypto]` 2.10.x y `PyJWKClient`, con caché/rotación
de JWKS del proveedor. El algoritmo permitido inicial es `RS256`; nunca se toma
la lista de algoritmos desde el token.

## Flujo

1. Presentation extrae un esquema `Bearer` del header `Authorization`.
2. El adaptador selecciona la clave por `kid` y verifica firma, `issuer`,
   `audience`, `exp`, `iat`, `iss`, `sub` y `aud`.
3. La pareja verificada `issuer + sub` se resuelve mediante el contrato público
   de Usuarios.
4. Solo un Usuario interno existente produce `ContextoIdentidad`.
5. Para una ruta tenant-scoped, Membresías deriva después `ContextoTaller`.

`PyJWKClient` es síncrono, por lo que descarga/verificación se ejecuta fuera del
event loop. Las pruebas inyectan dobles de JWKS/decoder y nunca acceden a red.

## Denegaciones

Token ausente, esquema incorrecto, firma inválida, token expirado, emisor o
audiencia incorrectos, claims obligatorios ausentes e identidad sin Usuario
interno producen `401` con mensaje seguro. No se registran tokens, claims
completos, payloads ni datos personales.

El mapeo `issuer + sub` implementa BR-021 y la política HTTP implementa AC-023.

MFA, recuperación de cuenta, refresh tokens y configuración del cliente Auth0
quedan fuera del backend fase 1.
