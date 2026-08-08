# Usuarios

**Fase:** 1 · **Estado del módulo:** Confirmado · **Contrato MVP:** Aceptado

## Propósito

Representar la identidad interna de las personas que usan la plataforma
(RF-USU-001 y RF-USU-002), separada de sus Membresías.

## Modelo aceptado

`Usuario` contiene:

- `id`: identificador interno opaco.
- `issuer` y `subject`: identificadores de la cuenta JWT local.
- `nombre`: nombre obligatorio.
- `nombre_usuario`: identificador público global, obligatorio y único.

`nombre_usuario` se normaliza eliminando espacios exteriores y un `@` inicial,
y convirtiendo a minúsculas. Su forma canónica tiene entre 3 y 30 caracteres y
solo acepta letras ASCII minúsculas, números, punto y guion bajo:
`^[a-z0-9._]{3,30}$` (BR-015).

La combinación `issuer + subject` es única y enlaza una identidad JWT
verificada con un único Usuario interno (BR-021). La contraseña se almacena
únicamente como hash scrypt.

## Casos de uso aceptados

- Registrar una cuenta local y emitir un JWT:
  `POST /api/v1/auth/registro`.
- Iniciar sesión con una cuenta local:
  `POST /api/v1/auth/login`.
  `POST /api/v1/usuarios/me`.
- Consultar el perfil actual: `GET /api/v1/usuarios/me`.
- Editar `nombre` o `nombre_usuario`: `PATCH /api/v1/usuarios/me`.
- Resolver mediante contrato público un Usuario por identidad JWT o por
  `nombre_usuario`, para consumidores autorizados como autenticación y
  Membresías.

Una identidad no registrada no construye contexto interno. Una colisión de
identidad o `nombre_usuario` produce conflicto seguro; la unicidad se refuerza
con índices MongoDB, no solo con comprobaciones previas.

## Límites

Usuarios no administra pertenencia, roles, permisos, Talleres ni Clientes. No
conoce FastAPI o MongoDB en Domain/Application. Sus contratos públicos exponen
solo la vista mínima que requieren autenticación y Membresías.

Usuario es global a la plataforma, no un dato tenant. Cualquier operación dentro
de un Taller requiere además una Membresía y un `ContextoTaller` autorizado
(BR-002, BR-014).

## Persistencia y consultas

Colección lógica `usuarios`, con índices únicos sobre `(issuer, subject)` y
`nombre_usuario`. Los identificadores cruzan Domain/Application como `str`
opacos; ningún documento MongoDB sale del adaptador.

## Aceptación y trazabilidad

- AC-016: identidad OIDC única, normalización, límites y colisión global de
  `nombre_usuario`.
- AC-013: independencia de capas y consumo mediante contratos públicos.
- AC-014: pruebas unitarias, API, tipos y estilo.

## Fuera de alcance

Contraseñas, desactivación, recuperación de cuenta, eliminación de Usuario,
invitaciones y aceptación pendiente.
