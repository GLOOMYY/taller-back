# Criterios de aceptación

Estos criterios son **Aceptados** para evaluar futuras entregas dentro de su fase.

| ID | Criterio |
|---|---|
| AC-001 | Una operación de Taller solo puede leer o modificar datos del contexto tenant autorizado (BR-007, BR-014; RNF-001, RNF-002). |
| AC-002 | Un Usuario puede vincularse a más de un Taller sin duplicar su identidad por ese motivo (RF-MEM-002). |
| AC-003 | Un Taller puede vincularse a más de un Usuario mediante Membresías (RF-MEM-002). |
| AC-004 | Membresía se modela y trata como concepto del dominio, sin reducirla a detalle accidental de persistencia (RF-MEM-001). |
| AC-005 | Un Cliente de un Taller no se comparte automáticamente con otro Taller (BR-005, BR-006; RF-CLI-001). |
| AC-006 | Un Dispositivo queda limitado a su Taller y asociado conceptualmente a un Cliente (BR-008; RF-DIS-001). |
| AC-007 | Dos visitas del mismo Dispositivo pueden registrarse como dos Órdenes independientes y consultarse como parte de su historia (BR-009, BR-010; RF-DIS-002, RF-ODS-001, RF-ODS-002). |
| AC-008 | Tipos, Marcas y Modelos son tenant-aware, validan unicidad normalizada y no permiten seleccionar inactivos o referencias cruzadas (RF-TDI-001, RF-TDI-002). |
| AC-009 | Tipos de servicio gestionan nombre único, descripción, precio predeterminado y estado activo por Taller (RF-TSE-001). |
| AC-010 | Pagos soporta fases sucesivas, división entre métodos, saldo, anulación y protección transaccional de sobrepago (RF-PAG-001 a RF-PAG-004). |
| AC-011 | Fase 2 incluye Proveedores e inventario mínimo de Repuestos, pero no Compras, cuentas por pagar ni lotes (RF-PRO-001, RF-INV-001, RF-INV-002). |
| AC-012 | Reportes no escribe ni posee la fuente canónica de los datos que presenta (BR-013; RF-REP-002). |
| AC-013 | Las dependencias respetan la dirección definida y no conectan módulos mediante internals o colecciones ajenas (RNF-003, RNF-007). |
| AC-014 | El código Python futuro supera los controles acordados de estilo, tipos, docstrings y pruebas (RNF-005). |
| AC-015 | La entrega no introduce módulos, reglas, campos, estados, endpoints o integraciones como Confirmados sin aprobación trazable. |
| AC-016 | Una cuenta JWT local puede registrar un único Usuario interno; `issuer + sub` y el `nombre_usuario` normalizado son únicos globalmente. |
| AC-017 | El creador de un Taller queda como dueño en la misma transacción y nunca se observa un Taller creado sin dueño. |
| AC-018 | Dueños y técnicos pueden editar Taller y gestionar Clientes, pero un técnico miembro recibe denegación al administrar Membresías. |
| AC-019 | Añadir una Membresía exige un `nombre_usuario` registrado y no permite duplicar el vínculo Usuario–Taller. |
| AC-020 | Retirar o degradar al último dueño produce conflicto y conserva el estado anterior. |
| AC-021 | Crear, listar, consultar y editar Clientes aplica el Taller autorizado; un identificador de otro Taller no revela su existencia. |
| AC-022 | Los listados usan cursor determinista, límite 20 por defecto y máximo 100, sin permitir que el cursor cambie el Taller. |
| AC-023 | La API responde `401` a identidad ausente/inválida, `404` a Taller/recurso inaccesible, `403` a un técnico miembro que administra Membresías, `409` a conflictos y `422` a entrada inválida. |
| AC-024 | Países y Monedas se leen con códigos y nombres legibles; Monedas incluye símbolo y decimales, sin escritura desde la API (RF-REF-001). |
| AC-025 | Crear Taller exige país/moneda válidos y confirma Taller, dueño y `Efectivo` o revierte todo; cambiar país/moneda no modifica Órdenes anteriores (RF-TAL-001, RF-TAL-003). |
| AC-026 | Un Dispositivo se crea/lista bajo su Cliente; `cliente_id` no cambia, no existe borrado y varias Órdenes activas pueden referirlo (RF-DIS-001, RF-DIS-002). |
| AC-027 | Los consecutivos de Orden son únicos bajo creación concurrente dentro de cada Taller y no tienen que ser globales (RF-ODS-001). |
| AC-028 | Solo se aceptan las transiciones de BR-032; `entregado` exige saldo cero y bloquea toda mutación ordinaria (RF-ODS-002). |
| AC-029 | Una reapertura por garantía exige Orden entregada y motivo, registra historial, habilita operación/finanzas y oculta el PDF hasta nueva entrega (RF-ODS-005, RF-CMP-001). |
| AC-030 | Servicios y Repuestos conservan snapshots; subtotal, descuento fijo/porcentaje y total se calculan con Decimal y nunca dejan total menor que lo pagado (RF-ODS-003). |
| AC-031 | El historial append-only contiene creación, campos, estados, garantía, servicios, Repuestos, descuentos, Pagos/anulaciones y pagina con cursor tenant-bound (RF-ODS-004). |
| AC-032 | Entradas aceptan Proveedor opcional; ajustes exigen motivo; todos generan movimiento y nunca producen existencia negativa (RF-INV-001). |
| AC-033 | Consumo concurrente insuficiente falla sin stock, movimiento, línea o historial parcial; retirar la línea antes de entrega restaura stock atómicamente (RF-INV-002). |
| AC-034 | Cada Pago cuadra total y líneas, usa solo métodos activos del Taller y no supera el saldo aun con solicitudes concurrentes (RF-PAG-002, RF-PAG-004). |
| AC-035 | Un Pago confirmado no se edita ni borra; su anulación única antes de entrega exige motivo, restaura saldo y registra historial (RF-PAG-003). |
| AC-036 | Los importes API son strings decimales, se persisten como Decimal128 y se cuantizan según el snapshot ISO con ROUND_HALF_UP (BR-045). |
| AC-037 | Un token de seguimiento válido revela solo el DTO aprobado; un token alterado, revocado o anterior a rotación no concede acceso (RF-SEG-001, RF-SEG-002). |
| AC-038 | El seguimiento no expone IDs sin firma, precios unitarios, métodos, abonos, Proveedores ni costos; sí expone el total final y muestra líneas de servicio como `Domicilio` cuando existan (RF-SEG-002). |
| AC-039 | El PDF solo existe para una Orden entregada, contiene total final, coincide con el DTO público y se genera fuera del event loop (RF-CMP-001). |
| AC-040 | Todas las entradas HTTP, casos de uso, repositorios y generación externa de fase 2 son asíncronos; bibliotecas bloqueantes se ejecutan fuera del event loop. |
| AC-041 | Índices, transacciones, rollback, Decimal128 y concurrencia se verifican contra MongoDB real con replica set, junto con API/OpenAPI, arquitectura, Ruff, formato y mypy. |
