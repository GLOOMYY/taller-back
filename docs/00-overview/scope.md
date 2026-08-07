# Alcance

## Dentro del alcance confirmado

- Arquitectura multi-tenant por Taller y Membresía.
- Fase 1: Usuarios, Talleres, Membresías y Clientes.
- Fase 2: referencias ISO, ampliación de Talleres, catálogos técnicos,
  Dispositivos, Tipos de servicio, Órdenes, Proveedores, inventario mínimo de
  Repuestos, Pagos, seguimiento público y comprobantes PDF.
- Fase 3: Compras y evolución del abastecimiento/inventario más allá del stock
  mínimo adelantado a fase 2.
- Fase 4: Reportes.
- Persistencia futura en MongoDB, modelada por agregados y patrones de consulta.
- Estándares arquitectónicos, de desarrollo, seguridad y pruebas descritos aquí.
- MVP local de fase 1 con FastAPI, MongoDB, OIDC, pruebas y CI.

## Fuera del alcance actual

- Interfaces visuales, incluido el frontend público imprimible.
- Compras completas, cuentas por pagar, inventario por lotes y devoluciones.
- Impuestos, facturación electrónica/fiscal, reembolsos y conversión monetaria.
- Hosting, TLS, backups, SLO, alertas y operación de producción.
- Invitaciones, eliminación de Talleres o Clientes, autoabandono y recuperación.

## Conceptos no confirmados como módulos

Notificaciones, Auditoría general y Archivos son **Candidatos/Pendientes**.
Diagnóstico, reparación/trabajo realizado, garantía y entrega se aceptan como
conceptos internos de Órdenes y no como módulos separados.

## Control del alcance

Una necesidad nueva debe registrarse primero como **Propuesta** o **Pendiente**, recibir definición y aceptación explícita, y solo después incorporarse como requisito con identificador.
