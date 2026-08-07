# Permisos

## Matriz aceptada

| Capacidad | `dueno` | `tecnico` |
|---|---:|---:|
| Consultar y editar Taller | Sí | Sí |
| Crear, listar, consultar y editar Clientes | Sí | Sí |
| Listar Membresías | Sí | Sí |
| Agregar Usuario existente por arroba | Sí | No |
| Cambiar rol de miembro | Sí | No |
| Retirar miembro | Sí | No |
| Referencias de solo lectura | Sí | Sí |
| Catálogos, Dispositivos y Tipos de servicio de fase 2 | Sí | Sí |
| Órdenes, garantía e historial | Sí | Sí |
| Proveedores, Repuestos y movimientos | Sí | Sí |
| Métodos, Pagos y anulaciones | Sí | Sí |
| Habilitar, rotar o revocar seguimiento | Sí | Sí |

Se deniega por defecto cualquier capacidad no listada. Los permisos se evalúan
en el rol de la Membresía del Taller actual, nunca en el Usuario global.

## Reglas adicionales

- Crear Taller crea al Usuario autenticado como `dueno` atómicamente.
- Ninguna operación puede retirar o degradar al último dueño.
- Agregar exige un Usuario ya registrado y una pareja Taller–Usuario no existente.
- No hay administrador global, permisos personalizados, invitaciones, jerarquía
  de roles ni autoabandono en fase 1.

Dueños y técnicos tienen las mismas capacidades operativas de fase 2. La única
diferencia vigente continúa siendo administración de Membresías. La matriz
traza BR-016 a BR-019, RF-MEM-001 a RF-MEM-004 y los RF de fase 2.
