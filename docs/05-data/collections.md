# Colecciones aceptadas — fases 1 y 2

La fase 1 usa colecciones compartidas en una base MongoDB. Cada módulo es el
único propietario de sus escrituras y ningún adaptador consulta colecciones
ajenas directamente.

## `usuarios`

Propietario: Usuarios. Documento de identidad interna con `issuer`, `subject`,
`nombre_usuario` normalizado y `nombre`. Sus restricciones globales se soportan
con índices únicos para `(issuer, subject)` y `nombre_usuario`.

## `talleres`

Propietario: Talleres. Documento con `_id` y `nombre`. Es la raíz de la frontera
tenant; no se embeben Membresías porque crecen y se consultan por ambos lados.

## `membresias`

Propietario: Membresías. Referencia `taller_id`, `usuario_id` y rol `dueno` o
`tecnico`. La creación inicial se confirma en la misma transacción que Taller.
La unicidad `(taller_id, usuario_id)` evita vínculos duplicados.

## `clientes`

Propietario: Clientes. Un documento representa un Cliente local del Taller:

```javascript
{
  _id: ObjectId,
  taller_id: "<id opaco de Taller>",
  nombre: "Isabella",
  telefono: "opcional",
  correo: "opcional",
  notas: "opcional"
}
```

`taller_id` y `nombre` son obligatorios. Los campos opcionales ausentes no se
persisten; una edición con `null` los elimina mediante `$unset`. No existe
unicidad por datos personales, embedding en Taller ni borrado en fase 1.

Patrones soportados:

- insertar con `taller_id` derivado del contexto;
- listar por `taller_id`, orden ascendente determinista por `_id` y cursor;
- consultar por `(taller_id, _id)`;
- editar por `(taller_id, _id)`.

Los documentos pueden contener datos personales. No se registran payloads,
nombres, teléfonos, correos ni notas en logs. Retención, cifrado por campo y
migraciones de producción siguen fuera del MVP local.

## Colecciones de fase 2

Todas las operativas incluyen `taller_id`; IDs externos son strings opacos. Los
campos listados definen el mínimo contractual, no una serialización pública.

| Colección | Propietario | Contenido/patrón principal |
|---|---|---|
| `paises` | Referencias | código ISO y nombre; lectura global |
| `monedas` | Referencias | código ISO, nombre, símbolo y decimales; lectura global |
| `tipos_dispositivo` | Catálogo técnico | nombre normalizado y activo por Taller |
| `marcas_dispositivo` | Catálogo técnico | nombre normalizado y activo por Taller |
| `modelos_dispositivo` | Catálogo técnico | Tipo, Marca, nombre normalizado y activo por Taller |
| `dispositivos` | Dispositivos | Cliente inmutable, Modelo, identificador y notas |
| `tipos_servicio` | Tipos de servicio | nombre, descripción, precio predeterminado y activo |
| `ordenes` | Órdenes | Dispositivo, consecutivo, snapshot moneda, estado, campos, líneas, descuento y versión pública |
| `ordenes_historial` | Órdenes | eventos append-only paginables |
| `contadores_orden` | Órdenes | siguiente consecutivo atómico por Taller |
| `proveedores` | Proveedores | nombre, contacto, notas y activo |
| `repuestos` | Inventario | código, nombre, descripción, precio, existencia y activo |
| `movimientos_inventario` | Inventario | entrada, ajuste, consumo o reversión append-only |
| `metodos_pago` | Pagos | nombre normalizado y activo |
| `pagos` | Pagos | Orden, total/líneas Decimal128 y anulación append-only lógica |
| `cuentas_financieras_orden` | Pagos/contrato transaccional | total, pagado y saldo serializados por Orden |

Las líneas de servicio/Repuesto se embeben en Orden porque se leen con ella,
son snapshots de ese ciclo de vida y sus mutaciones se coordinan con las
colecciones propietarias cuando hay stock. Historial, movimientos y Pagos se
referencian porque crecen sin límite y se consultan/paginan por separado.

El token público nunca se persiste. Orden conserva únicamente habilitación y
versión necesarias para verificar/revocar. No existen colecciones de Compras,
facturas, impuestos, lotes, cuentas por pagar o comprobantes PDF.
