# Índices aceptados

## Índices aceptados

| Colección | Clave | Opciones | Patrón que soporta |
|---|---|---|---|
| `usuarios` | `issuer`, `subject` | único | mapear identidad OIDC a un Usuario |
| `usuarios` | `nombre_usuario` | único | registro global y alta de miembro por `@` |
| `membresias` | `taller_id`, `usuario_id` | único | evitar Membresía duplicada y resolver acceso |
| `membresias` | `usuario_id`, `taller_id` | no único | listar Talleres accesibles por Usuario |
| `clientes` | `taller_id`, `_id` | no único | listar por Taller y cursor `_id`; consulta tenant-aware |

MongoDB también mantiene su índice único `_id_`. La clave compuesta de
Clientes hace explícito el prefijo tenant del patrón de listado; los filtros de
consulta y edición incluyen siempre `taller_id`, aun cuando el planificador
pueda seleccionar `_id_` por su alta selectividad.

## Reglas

- Los índices no sustituyen el filtro tenant ni la autorización.
- No existe índice único sobre nombre, teléfono o correo de Cliente.
- Cada adaptador crea únicamente los índices de su colección propietaria.
- Las pruebas de integración verifican nombre y claves de los índices contra
  MongoDB real. Antes de producción se revisarán planes de ejecución y volumen
  representativo.

## Fase 2

Todo índice operativo listable comienza por `taller_id`.

| Colección | Clave | Opciones/propósito |
|---|---|---|
| `paises` | `codigo` | único global |
| `monedas` | `codigo` | único global |
| `tipos_dispositivo` | `taller_id`, `nombre_normalizado` | único |
| `marcas_dispositivo` | `taller_id`, `nombre_normalizado` | único |
| `modelos_dispositivo` | `taller_id`, `tipo_id`, `marca_id`, `nombre_normalizado` | único |
| `dispositivos` | `taller_id`, `cliente_id`, `_id` | listar bajo Cliente |
| `dispositivos` | `taller_id`, `_id` | consulta tenant-aware |
| `tipos_servicio` | `taller_id`, `nombre_normalizado` | único |
| `ordenes` | `taller_id`, `consecutivo` | único por Taller |
| `ordenes` | `taller_id`, `dispositivo_id`, `_id` | historia/listado |
| `ordenes_historial` | `taller_id`, `orden_id`, `_id` | cursor append-only |
| `contadores_orden` | `taller_id` | único, incremento atómico |
| `proveedores` | `taller_id`, `_id` | listado/consulta |
| `repuestos` | `taller_id`, `codigo` | único parcial cuando código existe |
| `repuestos` | `taller_id`, `_id` | listado/consulta |
| `movimientos_inventario` | `taller_id`, `repuesto_id`, `_id` | cursor append-only |
| `metodos_pago` | `taller_id`, `nombre_normalizado` | único |
| `pagos` | `taller_id`, `orden_id`, `_id` | listado de Pagos |
| `cuentas_financieras_orden` | `taller_id`, `orden_id` | único, serialización |

La desactivación no libera nombres/códigos únicos históricos. Las pruebas reales
verifican índices y conflictos concurrentes, no solo dobles en memoria.
