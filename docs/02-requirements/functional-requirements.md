# Requisitos funcionales

Todos los requisitos de esta tabla están **Aceptados** al nivel de detalle escrito. No implican CRUD, campos, estados, pantallas ni endpoints específicos.

| ID | Fase | Requisito |
|---|---:|---|
| RF-USU-001 | 1 | Registrar una cuenta JWT local con nombre, contraseña y `nombre_usuario` global único. |
| RF-USU-002 | 1 | Consultar y editar el perfil del Usuario autenticado. |
| RF-TAL-001 | 1–2 | Crear un Taller con nombre, país y moneda y confirmar atómicamente Taller, dueño y método `Efectivo`. |
| RF-TAL-002 | 1 | Listar, consultar y editar Talleres accesibles para el Usuario autenticado. |
| RF-MEM-001 | 1 | Representar la pertenencia Usuario–Taller mediante una Membresía con rol `dueno` o `tecnico`. |
| RF-MEM-002 | 1 | Permitir múltiples Talleres por Usuario y múltiples Usuarios por Taller. |
| RF-MEM-003 | 1 | Permitir a un dueño listar y añadir Usuarios existentes por `nombre_usuario`, cambiar roles y retirar miembros. |
| RF-MEM-004 | 1 | Impedir que un Taller quede sin dueño. |
| RF-CLI-001 | 1 | Crear y listar Clientes exclusivos dentro de un Taller autorizado. |
| RF-CLI-002 | 1 | Consultar y editar un Cliente dentro de su Taller autorizado, sin operación de borrado. |
| RF-REF-001 | 2 | Listar y consultar referencias ISO globales de Países y Monedas, de solo lectura. |
| RF-TAL-003 | 2 | Editar siempre el país y moneda de un Taller sin alterar snapshots de Órdenes existentes. |
| RF-TDI-001 | 2 | Crear, listar, consultar, editar y activar/desactivar Tipos, Marcas y Modelos tenant-scoped. |
| RF-TDI-002 | 2 | Validar nombres normalizados únicos y la pertenencia Tipo–Marca–Modelo al mismo Taller. |
| RF-DIS-001 | 2 | Crear y listar Dispositivos bajo Cliente y consultarlos/editarlos bajo Taller. |
| RF-DIS-002 | 2 | Mantener Cliente inmutable, impedir borrado/reasignación y permitir múltiples Órdenes activas. |
| RF-TSE-001 | 2 | Gestionar Tipos de servicio tenant-scoped con descripción, precio predeterminado y estado activo. |
| RF-ODS-001 | 2 | Crear y consultar Órdenes con ID opaco, consecutivo atómico, Dispositivo, falla y snapshot monetario. |
| RF-ODS-002 | 2 | Editar parcialmente campos operativos y ejecutar únicamente las transiciones de estado aceptadas. |
| RF-ODS-003 | 2 | Agregar y retirar líneas snapshot de servicios y Repuestos y aplicar/quitar descuento global. |
| RF-ODS-004 | 2 | Mantener historial append-only paginado de toda mutación operativa y financiera de la Orden. |
| RF-ODS-005 | 2 | Reabrir una Orden entregada por garantía mediante una acción explícita y motivo obligatorio. |
| RF-PRO-001 | 2 | Crear, listar, consultar, editar y activar/desactivar Proveedores del Taller. |
| RF-INV-001 | 2 | Gestionar Repuestos, existencia entera y entradas/ajustes con movimientos append-only. |
| RF-INV-002 | 2 | Consumir o reponer Repuestos al agregar o retirar líneas de una Orden mediante transacciones. |
| RF-PAG-001 | 2 | Gestionar Métodos de pago tenant-scoped, incluido `Efectivo` inicial, con desactivación lógica. |
| RF-PAG-002 | 2 | Registrar múltiples Pagos por Orden con una o varias líneas de método y cálculo de saldo. |
| RF-PAG-003 | 2 | Anular antes de entrega un Pago confirmado mediante motivo, sin editarlo ni borrarlo. |
| RF-PAG-004 | 2 | Serializar total, Pagos, anulaciones y entrega mediante cuenta financiera por Orden. |
| RF-SEG-001 | 2 | Habilitar, rotar y revocar seguimiento público firmado sin almacenar tokens. |
| RF-SEG-002 | 2 | Exponer JSON público limitado de seguimiento sin precios unitarios ni datos financieros sensibles. |
| RF-CMP-001 | 2 | Descargar comprobante PDF desde el DTO público únicamente mientras la Orden esté entregada. |
| RF-COM-001 | 3 | El sistema contemplará Compras en la fase 3. |
| RF-REP-001 | 4 | El sistema contemplará Reportes en la fase 4. |
| RF-REP-002 | 4 | Reportes consumirá datos sin convertirse en fuente de verdad. |

## No requisitos

Diagnóstico, trabajo realizado, garantía y entrega son conceptos internos de
Órdenes, no módulos independientes. Compras completas, obligaciones a
Proveedores, lotes, fiscalidad, reembolsos, conversión, frontend público,
Notificaciones, Auditoría general y Archivos no son requisitos de fase 2.
