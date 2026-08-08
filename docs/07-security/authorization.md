# Autorización

## Modelo aceptado para fase 1

Autenticación no implica acceso a Talleres. Toda operación tenant-scoped recibe
un `ContextoTaller` derivado en servidor al cruzar el `usuario_id` interno, el
`taller_id` del path y una Membresía persistida. Nunca se confía únicamente en
el path (BR-014, BR-017, RNF-002, AC-001 y AC-018).

Los dos roles están contenidos en cada Membresía:

- `dueno`: Taller, Clientes y administración de Membresías.
- `tecnico`: Taller y Clientes; no administra Membresías.

No existe un rol global ni herencia de permisos entre Talleres. Un mismo Usuario
puede tener roles distintos en Talleres diferentes.

## Orden de controles

1. Verificar JWT y resolver Usuario interno (`ContextoIdentidad`).
2. Resolver la Membresía exacta `(taller_id, usuario_id)`.
3. Construir `ContextoTaller` con el rol persistido.
4. Comprobar la capacidad antes de consultar o mutar el recurso.
5. Mantener el filtro tenant también en el repositorio y validar referencias.

## Política de errores aceptada

- `401`: token ausente/inválido o identidad sin Usuario interno.
- `404`: Taller/recurso sin acceso, inexistente o perteneciente a otro tenant.
- `403`: un técnico miembro intenta administrar Membresías de ese Taller.
- `409`: Membresía duplicada o mutación que dejaría el Taller sin dueño.
- `422`: entrada que no satisface el contrato.

La diferencia `403`/`404` solo se revela después de comprobar una Membresía
del Taller solicitado (AC-023).
