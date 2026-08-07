# Endpoints aceptados — fase 2

Base autenticada tenant-scoped:
`/api/v1/talleres/{taller_id}`. Dueños y técnicos tienen las mismas capacidades
de fase 2. El servidor deriva `ContextoTaller` desde JWT y Membresía y valida
toda referencia; un ID cross-tenant se comporta como ausente.

Listados usan `limite` (20 por defecto, 100 máximo), `cursor`, respuesta
`{items, siguiente_cursor}` y cursores tenant-bound. IDs son opacos. PATCH es
parcial; omitido conserva y `null` limpia solo opcionales.

## Referencias y Taller

| Método | Ruta | Capacidad |
|---|---|---|
| GET | `/api/v1/referencias/paises` | listar Países ISO |
| GET | `/api/v1/referencias/paises/{codigo}` | consultar País |
| GET | `/api/v1/referencias/monedas` | listar Monedas ISO |
| GET | `/api/v1/referencias/monedas/{codigo}` | consultar Moneda |
| POST | `/api/v1/talleres` | exige `nombre`, `pais_codigo`, `moneda_codigo`; crea dueño y `Efectivo` |
| PATCH | `/api/v1/talleres/{taller_id}` | editar nombre, país o moneda |
| GET | `/api/v1/talleres/{taller_id}/resumen-operativo` | métricas del periodo calculadas por el backend |

Referencias requieren autenticación pero no Taller y son de solo lectura. No se
valida correspondencia país–moneda.

El resumen usa 30 días por defecto mediante `periodo_dias`; admite
`fecha_desde`/`fecha_hasta`. Devuelve conteos y series de Órdenes, junto con
totales y series de Pagos separados por moneda snapshot. Nunca suma ni convierte
monedas distintas y devuelve ceros/listas vacías cuando no existe actividad.

## Catálogos técnicos y servicios

Cada base permite `GET, POST`; cada `/{id}` permite `GET, PATCH, DELETE`. PATCH
incluye edición/reactivación y DELETE desactiva lógicamente sin borrar.

| Base | Entrada mínima de creación |
|---|---|
| `/tipos-dispositivo` | `nombre` |
| `/marcas-dispositivo` | `nombre` |
| `/modelos-dispositivo` | `tipo_id`, `marca_id`, `nombre` |
| `/tipos-servicio` | `nombre`, `precio_predeterminado`; `descripcion` opcional |

Nombres se normalizan y son únicos según BR-026/030. Elementos inactivos se
pueden consultar/editar, pero no seleccionar para nuevas relaciones.

## Dispositivos

| Método | Ruta | Capacidad |
|---|---|---|
| GET, POST | `/clientes/{cliente_id}/dispositivos` | listar/crear bajo Cliente |
| GET, PATCH | `/dispositivos/{dispositivo_id}` | consultar/editar equipo |

POST exige `modelo_id`; admite `identificador` y `notas`. PATCH no acepta
`cliente_id`. No existe DELETE.

## Órdenes

| Método | Ruta | Capacidad |
|---|---|---|
| GET, POST | `/ordenes` | listar/crear |
| GET, PATCH | `/ordenes/{orden_id}` | consultar/editar campos operativos |
| POST | `/ordenes/{orden_id}/transiciones` | aplicar `{estado_destino}` |
| POST | `/ordenes/{orden_id}/reapertura-garantia` | reabrir con `{motivo}` |
| POST | `/ordenes/{orden_id}/servicios` | agregar línea snapshot |
| DELETE | `/ordenes/{orden_id}/servicios/{linea_id}` | retirar línea |
| POST | `/ordenes/{orden_id}/repuestos` | consumir y agregar línea snapshot |
| DELETE | `/ordenes/{orden_id}/repuestos/{linea_id}` | retirar y reponer stock |
| PUT, DELETE | `/ordenes/{orden_id}/descuento` | fijar o quitar descuento global |
| GET | `/ordenes/{orden_id}/historial` | historial autenticado paginado |

Crear exige `dispositivo_id` y `falla_reportada`; captura moneda y asigna
consecutivo. PATCH admite diagnóstico, trabajo realizado, accesorios recibidos,
falla y notas. Una línea de servicio exige `tipo_servicio_id`, cantidad y precio
opcional; una de Repuesto exige `repuesto_id`, cantidad y precio opcional. El
descuento usa exactamente `{tipo: "fijo", monto}` o
`{tipo: "porcentaje", porcentaje}`. Importes son strings decimales.

GET `/ordenes` admite `estado`, `grupo`, `cliente_id`, `dispositivo_id` y
`texto`. `grupo` acepta `abiertas`, `pendientes_recogida` o `entregadas`; esos
conjuntos se resuelven en el backend y no se reconstruyen en el frontend.

## Proveedores e Inventario

| Método | Ruta | Capacidad |
|---|---|---|
| GET, POST | `/proveedores` | listar/crear |
| GET, PATCH | `/proveedores/{proveedor_id}` | consultar/editar/activar |
| GET, POST | `/repuestos` | listar/crear |
| GET, PATCH | `/repuestos/{repuesto_id}` | consultar/editar/activar |
| POST | `/repuestos/{repuesto_id}/entradas` | sumar stock |
| POST | `/repuestos/{repuesto_id}/ajustes` | ajustar stock con motivo |
| GET | `/repuestos/{repuesto_id}/movimientos` | listar movimientos paginados |

Entrada exige `cantidad`, `costo_unitario` y admite `proveedor_id`, `nota`.
Ajuste exige `delta` no cero y `motivo`. Stock insuficiente es `409` y no deja
efectos parciales.

Proveedores y Repuestos admiten `texto` y `activo`; DELETE los desactiva
lógicamente. Métodos de pago y catálogos también usan DELETE exclusivamente
para desactivación lógica.

## Métodos y Pagos

| Método | Ruta | Capacidad |
|---|---|---|
| GET, POST | `/metodos-pago` | listar/crear métodos |
| GET, PATCH, DELETE | `/metodos-pago/{metodo_id}` | consultar/editar/reactivar o desactivar lógicamente |
| GET, POST | `/ordenes/{orden_id}/pagos` | listar/confirmar Pagos |
| POST | `/pagos/{pago_id}/anulacion` | anular con `{motivo}` |

POST de Pago recibe `total` y `lineas`, cada una con `metodo_pago_id` y `monto`.
Pago confirmado es inmutable: no hay PATCH/DELETE. Anulación única solo antes de
entrega. Invariantes concurrentes devuelven `409` sin efecto parcial.

## Seguimiento público y comprobante

| Método | Ruta | Capacidad |
|---|---|---|
| POST | `/ordenes/{orden_id}/seguimiento` | habilitar y devolver token |
| POST | `/ordenes/{orden_id}/seguimiento/rotacion` | rotar y devolver nuevo token |
| DELETE | `/ordenes/{orden_id}/seguimiento` | revocar versión vigente |
| GET | `/api/v1/publico/seguimiento/{token}` | DTO público JSON |
| GET | `/api/v1/publico/seguimiento/{token}/comprobante.pdf` | PDF si `entregado` |

Las tres primeras requieren autenticación/contexto. Las públicas solo aceptan
token HMAC válido. El DTO JSON contiene estado, equipo, falla, diagnóstico,
trabajo, historial operativo, servicios/Repuestos sin unitarios y `total_final`.
Nunca contiene métodos, Pagos, Proveedores, costos o un ID de Orden sin firma.
El token no se registra ni persiste y permanece válido hasta revocar/rotar.

## Semántica transversal

- `401`: identidad autenticada ausente/inválida; `404`: inaccesible/cross-tenant
  o token/PDF no disponible; `409`: unicidad, estado, stock o finanzas; `422`:
  forma/decimal/cursor inválido.
- No hay idempotencia contractual general. Las transacciones garantizan
  atomicidad e invariantes, no deduplican reintentos del cliente.
- No hay endpoints de borrado físico de Orden, Dispositivo, catálogos,
  Proveedor, Repuesto, Método o Pago.
