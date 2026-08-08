# Aislamiento de Talleres

## Amenaza principal

Lectura, modificación, inferencia o agregación de datos de un Taller desde el
contexto de otro.

## Controles aceptados

1. Verificar el JWT local y mapear `issuer + sub` a un Usuario interno.
2. Resolver la Membresía con ambos `taller_id` y `usuario_id` del contexto.
3. Construir y pasar `ContextoTaller` explícito a cada caso de uso tenant-scoped.
4. Autorizar la capacidad según el rol de esa Membresía.
5. Aplicar `taller_id` en toda consulta, update, delete y agregación operativa.
6. Validar que las referencias pertenezcan al mismo Taller.
7. Traducir ausencia/cross-tenant a `404` sin revelar existencia.
8. Registrar solo IDs internos ya validados y correlación; nunca tokens,
   payloads completos o datos personales.
9. Probar con al menos dos Talleres y cruzar IDs reales entre ambos.

## Contratos de contexto

`ContextoIdentidad` contiene `usuario_id`, `issuer` y `subject` verificados.
`ContextoTaller` contiene `usuario_id`, `taller_id` y rol `dueno | tecnico`
obtenido del servidor. Presentation y Application pueden transportar estos
contratos; el cliente nunca los construye ni decide el rol.

Los IDs son strings opacos fuera de Infrastructure. MongoDB usa colecciones
compartidas e índices tenant-aware; esta estrategia no sustituye ningún control
lógico anterior.
