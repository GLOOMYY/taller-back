# Reglas de negocio

Este es el catálogo canónico. Todas las reglas listadas están **Confirmadas/Aceptadas** salvo indicación explícita.

| ID | Regla |
|---|---|
| BR-001 | Cada Taller constituye un tenant. |
| BR-002 | Un Usuario puede pertenecer a múltiples Talleres mediante Membresías. |
| BR-003 | Un Taller puede tener múltiples Usuarios mediante Membresías. |
| BR-004 | Membresía es un concepto de dominio, no una simple relación técnica. |
| BR-005 | Cada Cliente pertenece exclusivamente a un Taller. |
| BR-006 | La misma persona puede existir como Clientes independientes en Talleres distintos. |
| BR-007 | Todo dato operativo debe estar limitado al Taller y el aislamiento tenant es transversal. |
| BR-008 | Cada Dispositivo pertenece a un Taller y representa un aparato electrónico de un Cliente. |
| BR-009 | Un Dispositivo puede tener múltiples Órdenes de servicio a lo largo del tiempo. |
| BR-010 | Cada visita o trabajo se registra mediante una Orden de servicio independiente. |
| BR-011 | Tipo de dispositivo clasifica Dispositivos. |
| BR-012 | Tipo de servicio cataloga servicios ofrecidos por el Taller. |
| BR-013 | Reportes consume datos de módulos propietarios y no es fuente de verdad. |
| BR-014 | El contexto de Taller autorizado debe derivarse y validarse; nunca se confía únicamente en un `taller_id` enviado por el cliente. |
| BR-015 | Cada Usuario tiene un `nombre_usuario` globalmente único, normalizado a minúsculas y formado por 3–30 caracteres ASCII: letras, números, punto o guion bajo. |
| BR-016 | Al crear un Taller, su creador obtiene atómicamente una Membresía con rol `dueno`. |
| BR-017 | Una Membresía tiene exactamente uno de los roles `dueno` o `tecnico`. Dueños y técnicos administran el Taller y sus Clientes; solo los dueños administran Membresías. |
| BR-018 | Un dueño puede vincular un Usuario ya registrado mediante su `nombre_usuario`, cambiar su rol o retirarlo del Taller. |
| BR-019 | Un Taller debe conservar al menos una Membresía con rol `dueno`; no se permite retirar ni degradar al último dueño. |
| BR-020 | Un Cliente requiere nombre y puede registrar teléfono, correo y notas; siempre se crea, consulta y actualiza dentro de un Taller autorizado y no se elimina en fase 1. |
| BR-021 | La cuenta local de un Usuario se vincula de forma única mediante `sub` del JWT; la plataforma almacena únicamente un hash de contraseña. |
| BR-022 | Países y Monedas son catálogos ISO globales de solo lectura para la operación; exponen códigos y nombres legibles y, para Monedas, símbolo y cantidad de decimales. |
| BR-023 | Todo Taller requiere `pais_codigo` y `moneda_codigo`; ambos pueden cambiar y no se exige correspondencia entre país y moneda. |
| BR-024 | Crear un Taller confirma atómicamente Taller, Membresía inicial `dueno` y método de pago activo `Efectivo`. |
| BR-025 | Una Orden conserva un snapshot inmutable del código, símbolo y decimales de la moneda vigente en el Taller al crearla. |
| BR-026 | Tipo, Marca y Modelo de dispositivo son catálogos tenant-scoped activables/desactivables; sus nombres normalizados son únicos en su alcance y un Modelo es único por `(taller_id, tipo_id, marca_id, nombre_normalizado)`. |
| BR-027 | Un elemento de catálogo inactivo conserva referencias históricas pero no puede seleccionarse en nuevas relaciones. `DELETE` sobre catálogos o Métodos de pago desactiva lógicamente; no existe borrado físico. |
| BR-028 | Un Dispositivo pertenece al Cliente y Taller con que se crea; `cliente_id` es inmutable, no se reasigna ni se borra. Puede registrar `modelo_id`, identificador libre opcional y notas opcionales. |
| BR-029 | Pueden existir varias Órdenes activas simultáneas para un mismo Dispositivo. |
| BR-030 | Un Tipo de servicio pertenece a un Taller y contiene nombre único normalizado, descripción opcional, precio predeterminado y estado activo. |
| BR-031 | Cada Orden recibe un ID opaco y un consecutivo único asignado atómicamente dentro del Taller; exige Dispositivo y falla reportada y admite diagnóstico, trabajo realizado, accesorios recibidos y notas opcionales. |
| BR-032 | El ciclo normal de Orden permite `abierta → en_proceso`, `en_proceso ↔ espera_repuesto`, `en_proceso → pendiente_recogida` y `pendiente_recogida → entregado`; no se cancela ni se borra. |
| BR-033 | Entregar una Orden exige saldo cero. Una Orden `entregado` queda congelada para toda mutación ordinaria. |
| BR-034 | Una garantía reabre explícitamente la misma Orden `entregado → en_proceso` con motivo obligatorio, desbloquea operación y finanzas y luego usa el ciclo normal hasta una nueva entrega. |
| BR-035 | Las líneas de servicio y Repuesto de una Orden conservan snapshots de nombre, cantidad y precio; el precio puede ajustarse al agregar la línea. |
| BR-036 | El subtotal de una Orden es servicios más repuestos. El descuento global es fijo o porcentual y el total es subtotal menos descuento, cuantizado en la moneda de la Orden. Ninguna mutación puede dejar el total por debajo de lo pagado. |
| BR-037 | El historial de Orden es append-only y registra creación, cambios de campos y estado, garantía, servicios, repuestos, descuento, Pagos y anulaciones. |
| BR-038 | Un Proveedor pertenece a un Taller, tiene nombre, contacto y notas opcionales y estado activo; se desactiva, no se borra físicamente. |
| BR-039 | Un Repuesto pertenece a un Taller, tiene código opcional único dentro del Taller, nombre, descripción opcional, precio de venta, existencia entera y estado activo. |
| BR-040 | Las entradas suman una cantidad positiva con costo unitario, Proveedor opcional y nota; los ajustes usan delta no cero y motivo obligatorio. Ninguna operación deja existencia negativa. |
| BR-041 | Todo cambio de existencia crea un movimiento append-only: entrada, ajuste, consumo en Orden o reversión de consumo. Agregar o retirar un Repuesto de una Orden actualiza stock, movimiento e historial en una transacción. |
| BR-042 | Un Método de pago pertenece al Taller, tiene nombre único normalizado y estado activo; no tiene clasificación adicional y se desactiva sin borrado físico. |
| BR-043 | Una Orden admite múltiples Pagos reales sucesivos. Cada Pago tiene una o varias líneas `(metodo_pago_id, monto)` cuya suma coincide con su total y no supera el saldo vigente. |
| BR-044 | Un Pago confirmado es inmutable. Antes de entregar puede anularse con motivo obligatorio, una sola vez, restituyendo su importe al saldo. |
| BR-045 | Los importes cruzan la API como strings decimales, Domain como `Decimal` y MongoDB como `Decimal128`; se cuantizan con los decimales ISO del snapshot de moneda y `ROUND_HALF_UP`. |
| BR-046 | Las mutaciones concurrentes de total, Pagos, anulaciones y entrega se serializan transaccionalmente mediante una cuenta financiera por Orden, impidiendo sobrepago y entrega con saldo pendiente. |
| BR-047 | El seguimiento público usa un token HMAC firmado sobre Orden y versión, permanente hasta revocación o rotación. Solo revela el DTO público aprobado; el comprobante está disponible únicamente mientras la Orden está `entregado`. |

## Exclusiones de fase 2

- Invitaciones, aceptación pendiente, estados de Membresía, autoabandono y recuperación de cuentas quedan fuera de fase 1.
- Proveedores y entradas no constituyen Compras, cuentas por pagar o inventario
  por lotes.
- No hay impuestos, facturación electrónica, reembolsos, conversión de moneda,
  precios fiscales ni calendario previo de cobros.
- Garantía es una reapertura de la Orden original, no un módulo independiente.

Modificar una regla aceptada requiere una decisión explícita y revisión de los requisitos y criterios relacionados.
