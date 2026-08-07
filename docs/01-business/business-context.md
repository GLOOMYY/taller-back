# Contexto de negocio

## Contexto confirmado

La plataforma administra información de talleres de electrónica. El Taller es simultáneamente la unidad de negocio y la frontera tenant. Los Usuarios acceden a Talleres mediante Membresías; los Clientes y todos los datos operativos pertenecen a un Taller.

La operación se construirá incrementalmente:

- La base identifica quién participa, en cuál taller y qué clientes pertenecen a él.
- La operación principal conserva los dispositivos de clientes y registra cada visita o trabajo como una Orden de servicio independiente.
- La fase 2 incorpora Proveedores y existencias/movimientos mínimos de Repuestos
  para operar Órdenes; Compras y abastecimiento ampliado llegan después.
- Pagos reales sucesivos determinan saldo y entrega; el seguimiento público
  ofrece una vista limitada y comprobante cuando corresponde.
- Los reportes se derivan de los datos de los módulos propietarios.

## Límites aceptados de fase 2

BR-022 a BR-047 definen estados, campos mínimos, cálculos y concurrencia. No se
han definido Compras, lotes, cuentas por pagar, impuestos, facturación fiscal,
reembolsos, conversión monetaria, políticas de retención o producción.

## Riesgos de negocio a controlar

- Mezclar datos de dos Talleres.
- Confundir a una persona cliente de varios talleres con un registro global compartido.
- Perder la historia de un Dispositivo al registrar una nueva visita.
- Sobrevender Repuestos o confirmar sobrepagos por concurrencia.
- Exponer datos financieros mediante seguimiento público o logs de tokens.
- Convertir un Reporte en propietario de datos de negocio.
- Implementar fases futuras o candidatos como si fueran requisitos vigentes.
