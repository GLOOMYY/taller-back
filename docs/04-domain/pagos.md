# Pagos

**Fase:** 2 · **Estado:** Aceptado

## Métodos y Pagos

Método de pago es un catálogo tenant-scoped con nombre normalizado único y
`activo`; DELETE lo desactiva, no lo borra. `Efectivo` se crea con el Taller.

Una Orden admite múltiples Pagos reales sucesivos, sin calendario previo. Un
Pago confirmado contiene ID, Orden, total, líneas `(metodo_pago_id, monto)` y
moneda snapshot. La suma exacta de líneas coincide con
el total, usa Métodos activos del Taller y no excede el saldo.

## Inmutabilidad, anulación y cuenta financiera

Un Pago confirmado no se edita ni borra. Antes de `entregado` puede anularse
una sola vez con motivo obligatorio; la anulación se agrega sin reescribir sus
importes y repone saldo. La cuenta financiera por Orden materializa total,
pagado y saldo y serializa en transacción cambios de total, Pago, anulación y
entrega para impedir sobrepago.

Los importes usan string decimal en API, `Decimal` en dominio y `Decimal128` en
MongoDB, cuantizados según el snapshot de la Orden con `ROUND_HALF_UP`. No hay
impuestos, moneda múltiple, conversión, conciliación, reembolso ni fiscalidad.

Pagos recibe un contrato de Orden/cuenta dentro de la unidad transaccional y no
consulta la colección de Órdenes. Trazabilidad: BR-042 a BR-046;
RF-PAG-001 a RF-PAG-004; AC-034 a AC-036.
