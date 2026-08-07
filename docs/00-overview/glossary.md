# Glosario

| Término | Definición y estado |
|---|---|
| Usuario | **Confirmado.** Persona con identidad en la plataforma; puede pertenecer a varios Talleres. |
| Taller | **Confirmado.** Unidad de negocio y tenant del sistema. |
| Tenant | Frontera lógica de aislamiento; en este proyecto equivale a un Taller. |
| Membresía | **Confirmado.** Concepto de dominio que vincula Usuario y Taller. No es una mera relación técnica. |
| Cliente | **Confirmado.** Cliente registrado exclusivamente dentro de un Taller. La misma persona puede existir como registros independientes en talleres diferentes. |
| Dispositivo | **Confirmado.** Aparato electrónico de un Cliente, perteneciente a un Taller, cuya historia puede abarcar varias visitas. |
| Tipo de dispositivo | **Confirmado.** Catálogo tenant-scoped que encabeza la clasificación Tipo → Marca → Modelo. |
| Marca de dispositivo | **Confirmado para fase 2.** Segundo nivel del catálogo técnico de un Taller. |
| Modelo de dispositivo | **Confirmado para fase 2.** Modelo seleccionable dentro de un Tipo y una Marca del mismo Taller. |
| Orden de servicio | **Confirmado.** Registro independiente de una visita o trabajo sobre un Dispositivo. |
| Tipo de servicio | **Confirmado.** Catálogo tenant-scoped de servicios ofrecidos, con precio predeterminado. |
| Pago | **Confirmado para fase 2.** Abono real confirmado sobre una Orden, compuesto por una o varias líneas de método. |
| Método de pago | **Confirmado para fase 2.** Catálogo tenant-scoped de formas de recibir un Pago. |
| Saldo | **Confirmado para fase 2.** Total vigente de la Orden menos Pagos confirmados no anulados. |
| Repuesto | **Confirmado para fase 2.** Artículo inventariable del Taller con existencia entera y precio de venta. |
| Movimiento de inventario | **Confirmado para fase 2.** Registro append-only de entrada, ajuste, consumo o reversión de Repuesto. |
| Inventario | **Confirmado parcialmente para fase 2.** Existencias y movimientos de Repuestos; compras, lotes y valoración quedan para fases posteriores. |
| Proveedor | **Confirmado para fase 2.** Contraparte opcional de una entrada de stock, exclusiva del Taller. |
| Compra | **Confirmado para fase 3.** Módulo de compras; modelo y reglas pendientes. |
| Reporte | **Confirmado para fase 4.** Vista derivada que consume datos y no constituye fuente de verdad. |
| Seguimiento público | **Confirmado para fase 2.** Vista pública limitada de una Orden, accesible mediante token firmado, permanente y revocable. |
| Garantía | **Confirmado como operación de una Orden, no como módulo.** Reapertura explícita de una Orden entregada con motivo obligatorio. |
| Agregado | Frontera de consistencia del dominio, usada para orientar el modelado documental. |
| Puerto | Contrato que expresa una necesidad o capacidad sin acoplarse a una tecnología. |
| Adaptador | Implementación o interfaz que conecta un puerto con una tecnología o canal. |

Diagnóstico, trabajo realizado, garantía y entrega son conceptos de Órdenes, no
módulos independientes. Notificación, auditoría general y archivo no designan
módulos confirmados.
