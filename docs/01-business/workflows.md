# Flujos de negocio

Los siguientes flujos expresan relaciones y reglas aceptadas por fase.

## Acceso de Usuario a Taller

1. Existe un Usuario.
2. Existe un Taller.
3. Una Membresía representa su vínculo.
4. El contexto autorizado del Taller limita la operación.

Cumple BR-001 a BR-004, BR-007 y BR-014.

## Registro de Cliente

1. Una operación ocurre en el contexto de un Taller autorizado.
2. Se registra un Cliente exclusivo de ese Taller.
3. No se comparte automáticamente con otro Taller aunque represente a la misma persona.

Cumple BR-005 a BR-007.

## Historia de un Dispositivo

1. Un Dispositivo de un Cliente pertenece al Taller.
2. Una visita o trabajo crea una Orden de servicio independiente.
3. Una visita posterior crea otra Orden vinculada al mismo Dispositivo.
4. La secuencia de Órdenes conserva su trazabilidad.

Cumple BR-008 a BR-010.

## Apertura y operación de una Orden

1. Se valida que Dispositivo, Cliente y catálogos pertenezcan al Taller.
2. Se asigna consecutivo tenant-scoped y se captura el snapshot monetario.
3. La Orden se crea `abierta` con su evento de historial.
4. Las transiciones siguen BR-032; servicios y repuestos registran snapshots.
5. Consumos de Repuestos actualizan stock, movimiento e historial en una sola
   transacción.
6. Solo se entrega con saldo cero; al entregar queda congelada.

Cumple BR-025, BR-029 y BR-031 a BR-037.

## Reapertura por garantía

1. Una Orden `entregado` recibe una reapertura explícita con motivo.
2. Pasa a `en_proceso`, registra historial y vuelve a admitir operación/Pagos.
3. El comprobante público deja de estar disponible.
4. La Orden recorre de nuevo `pendiente_recogida → entregado` con saldo cero.

Cumple BR-033, BR-034 y BR-047.

## Stock de Repuestos

1. Una entrada o ajuste valida cantidad/delta y evita existencia negativa.
2. Se actualiza la existencia y se agrega el movimiento en una transacción.
3. Agregar Repuesto a Orden consume; retirarlo antes de entrega revierte.

Cumple BR-039 a BR-041.

## Pago de una Orden

1. Se valida Orden mutable, saldo y Métodos activos del mismo Taller.
2. Las líneas cuadran con el total del Pago y no exceden el saldo.
3. Pago, cuenta financiera e historial se confirman en una transacción.
4. Una anulación previa a entrega registra motivo y repone saldo sin editar el
   Pago original.

Cumple BR-042 a BR-046.

## Seguimiento y comprobante público

1. Un miembro habilita un token firmado para la versión de seguimiento.
2. El cliente consulta solo estado, equipo, contenido operativo, líneas sin
   precios unitarios, historial operativo y total final.
3. El PDF consume el mismo DTO público y solo se genera si está entregado.
4. Revocar o rotar invalida la versión anterior sin almacenar ni registrar el
   token.

Cumple BR-047.

## Abastecimiento completo y reportes

Compras, cuentas por pagar, lotes, valoración y Reportes permanecen fuera de
fase 2. El inventario mínimo anterior no constituye un flujo de Compras.
