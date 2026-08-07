# Membresías

**Fase:** 1 · **Estado del módulo:** Confirmado · **Contrato:** Aceptado

## Propósito

Representar y administrar el vínculo de dominio entre un Usuario y un Taller.
La Membresía es la fuente para derivar autorización tenant; recibir un
`taller_id` del cliente nunca demuestra acceso (RF-MEM-001 a RF-MEM-004;
BR-002, BR-003, BR-004, BR-014 y BR-016 a BR-019; AC-001 a AC-004 y
AC-017 a AC-020).

## Modelo mínimo aceptado

Una Membresía contiene IDs opacos de Membresía, Taller y Usuario, y exactamente
uno de estos roles:

- `dueno`: administra Membresías y, al igual que un técnico, puede administrar
  el Taller y sus Clientes.
- `tecnico`: puede administrar el Taller y sus Clientes, pero no Membresías.

Existe como máximo una Membresía para cada par `(taller_id, usuario_id)`. Un
Usuario puede pertenecer a varios Talleres y un Taller puede tener varios
Usuarios.

## Casos de uso aceptados

- Crear la Membresía `dueno` del creador dentro de la misma transacción que
  crea el Taller.
- Listar los miembros de un Taller autorizado con cursor determinista, límite
  predeterminado 20 y máximo público 100.
- Agregar como `dueno` o `tecnico` a un Usuario ya registrado, resolviéndolo por
  su `nombre_usuario` global normalizado.
- Cambiar el rol de un miembro.
- Retirar un miembro.

Invitaciones, aceptación pendiente, autoabandono, eliminación del Taller y
recuperación de cuentas no forman parte de fase 1.

## Invariantes y autorización

- Solo un `dueno` puede agregar, cambiar rol o retirar miembros.
- Un Taller nunca puede quedar sin al menos un `dueno`. La comprobación y la
  mutación deben ejecutarse atómicamente en MongoDB.
- Para administrar Membresías se deriva primero `ContextoTaller` desde la
  identidad interna y el vínculo persistido.
- Un técnico que sí pertenece al Taller recibe prohibición; identidad sin
  Membresía y acceso cruzado se presentan como recurso no encontrado.
- El alta duplicada, degradar al último dueño o retirarlo son conflictos.
- Buscar un arroba que no corresponde a un Usuario registrado produce recurso
  no encontrado y no crea invitación implícita.

Estas reglas trazan BR-016 (dueño inicial atómico), BR-017 (roles y
capacidades), BR-018 (gestión por nombre de usuario) y BR-019 (protección del
último dueño), además de AC-017 a AC-020 y AC-023.

## Límites y contratos

Membresías consume de Usuarios solo los contratos públicos
`buscar_por_nombre_usuario` y `obtener_por_identidad`; no accede a su colección
ni a sus adaptadores. Talleres puede consumir la lista de IDs accesibles y el
participante transaccional que crea al dueño inicial. Ningún documento MongoDB
ni `ObjectId` cruza hacia Domain/Application/Presentation.

## Persistencia

La colección `membresias` usa IDs string opacos. Requiere unicidad compuesta
`(taller_id, usuario_id)` e índices para `(usuario_id, taller_id)` y
`(taller_id, rol)`. Consultar/listar/modificar/retirar siempre incluye el
`taller_id` autorizado. Las operaciones que pueden afectar al último dueño
requieren replica set y transacción.
