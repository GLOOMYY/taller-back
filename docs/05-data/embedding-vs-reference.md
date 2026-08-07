# Embedding frente a referencia

## Criterios aceptados

Considerar **embedding** cuando los datos comparten ciclo de vida, se leen juntos, tienen crecimiento acotado y requieren actualización atómica. Considerar **referencia** cuando tienen identidad/ciclo independientes, alta cardinalidad, crecimiento no acotado o acceso separado.

## Restricciones aceptadas

- No decidir por analogía con claves foráneas relacionales.
- No duplicar datos canónicos sin definir propiedad y consistencia.
- No embeber listas potencialmente ilimitadas.
- Toda referencia operativa debe preservar/verificar el mismo Taller cuando corresponda.

## Decisiones de fase 1

- Membresías se referencia mediante `taller_id` y `usuario_id`: tiene ciclo de
  vida, permisos, cardinalidad y consultas independientes por ambos lados.
- Clientes se almacena en documentos propios referenciados por `taller_id`: su
  conjunto tiene crecimiento no acotado, se lista/pagina y se consulta de forma
  independiente. No se embebe dentro de Taller.

## Decisiones de fase 2

- Orden referencia Dispositivo; no se embeben Órdenes porque tienen identidad,
  consulta y ciclo propios y un Dispositivo admite múltiples activas.
- Líneas de servicio/Repuesto se embeben como snapshots acotados por la Orden.
- Historial, movimientos y Pagos son colecciones referenciadas append-only por
  crecimiento no acotado y paginación independiente.
- Cuenta financiera se separa por Orden para constituir el punto de
  serialización de las invariantes monetarias concurrentes.
- Catálogos, Proveedores y Repuestos mantienen identidad/ciclo independientes.
- El comprobante no se persiste; se deriva del DTO público de Orden.

Compras y proyecciones de Reportes conservan su decisión pendiente.
