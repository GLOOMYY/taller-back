# ADR-007: Operación financiera de fase 2

- **Estado:** Aceptado
- **Fecha:** 2026-08-07

## Contexto

Órdenes admite líneas, descuento, múltiples abonos reales y métodos divididos.
Cambiar precios o descuentos y registrar Pagos concurrentes debe preservar que
total nunca sea menor que lo pagado, que no exista sobrepago y que solo se
entregue con saldo cero. El Taller puede cambiar moneda, pero una Orden no debe
cambiar su semántica monetaria histórica.

## Decisión

La Orden captura código, símbolo y decimales de la Moneda al crearla. API usa
strings decimales, Domain `Decimal` y MongoDB `Decimal128`; toda operación se
cuantiza con `ROUND_HALF_UP` según ese snapshot.

Subtotal es servicios más Repuestos; descuento global es fijo o porcentaje;
total es subtotal menos descuento. Una cuenta financiera por Orden materializa
total, pagado y saldo y es el punto de serialización de mutaciones financieras.

Cada Pago representa un abono real confirmado, no una cuota planificada. Puede
dividirse en varias líneas de Método cuya suma exacta es el total. Confirmado es
inmutable; una anulación previa a entrega agrega motivo/estado y resta su monto
de pagado sin editar los importes originales.

## Alternativas descartadas

- `float` o números JSON: no preservan precisión decimal contractual.
- Inferir moneda actual del Taller: alteraría interpretación histórica.
- Calcular siempre saldo agregando Pagos sin documento coordinador: no ofrece
  un punto sencillo de serialización frente a cambios concurrentes de total.
- Calendario previo de fases/cuotas: no existe requisito actual.

## Consecuencias

- Todas las mutaciones de total/Pagos/anulación/entrega actualizan/verifican la
  cuenta dentro de transacción.
- No se admiten impuestos, conversión, reembolso, conciliación o fiscalidad.
- Índices y pruebas MongoDB reales deben verificar Decimal128 y concurrencia.
- Trazabilidad: BR-025, BR-035/036 y BR-042 a BR-046; AC-030 y AC-034 a AC-036.

