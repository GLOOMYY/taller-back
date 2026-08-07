# Órdenes de servicio

**Fase:** 2 · **Estado:** Aceptado

## Agregado y creación

Una Orden pertenece al Taller, referencia un Dispositivo, tiene ID opaco y
consecutivo tenant-scoped atómico. Requiere falla reportada y admite diagnóstico,
trabajo realizado, accesorios recibidos y notas opcionales. Captura código,
símbolo y decimales de la moneda vigente al crearla. Se crea `abierta` con su
cuenta financiera e evento inicial en una transacción.

## Estados y garantía

Transiciones únicas: `abierta → en_proceso`, `en_proceso ↔ espera_repuesto`,
`en_proceso → pendiente_recogida` y `pendiente_recogida → entregado`.
`entregado` exige saldo cero y congela toda mutación ordinaria. No hay cancelar
ni borrar. El endpoint explícito de garantía permite `entregado → en_proceso`
con motivo obligatorio; registra evento, desbloquea operación/finanzas e
invalida temporalmente el comprobante hasta la próxima entrega.

## Líneas, descuento y dinero

Una línea de servicio o Repuesto embebe snapshots de nombre, cantidad y precio
cuantizado, más la referencia de origen. Subtotal es la suma de líneas. Existe
un descuento global opcional, fijo o porcentual; total es subtotal menos
descuento. Ninguna mutación puede producir total negativo ni menor que Pagos
confirmados no anulados. Retirar Repuesto antes de entrega repone stock.

## Historial y concurrencia

El historial vive en colección propia append-only y registra creación, PATCH
de campos, transiciones, garantía, líneas, descuento, Pagos y anulaciones. Se
consulta autenticado con cursor tenant-bound. PATCH es parcial y la última
escritura por campo prevalece; no hay versionado optimista general. Las
invariantes de stock/finanzas y entrega sí usan transacciones.

Órdenes consume contratos públicos de Dispositivos, catálogos, Inventario y
Pagos, nunca sus colecciones. El DTO público de seguimiento es una salida del
caso de uso de Orden.

Trazabilidad: BR-031 a BR-037, BR-046/047; RF-ODS-001 a RF-ODS-005;
AC-027 a AC-031.

