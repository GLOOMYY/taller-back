# Límites de módulos

## Módulos confirmados

| Fase | Módulos |
|---|---|
| 1 | Usuarios, Talleres, Membresías, Clientes |
| 2 | Referencias, Dispositivos, catálogo técnico, Órdenes, Tipos de servicio, Proveedores, Inventario de Repuestos, Pagos, Seguimiento/Comprobantes |
| 3 | Compras y evolución del abastecimiento/inventario |
| 4 | Reportes |

## Propiedad y colaboración

- Un módulo modifica únicamente su propio estado mediante su capa Application.
- Las referencias entre módulos usan identificadores y contratos públicos
  explícitos; una unidad de trabajo compone transacciones cross-module sin
  permitir que un módulo consulte colecciones ajenas.
- El consumidor no depende de entidades internas, documentos MongoDB ni adaptadores del proveedor.
- Reportes solo consume datos mediante contratos aprobados.
- La validación tenant no se delega implícitamente a un módulo vecino.

## Relaciones conceptuales confirmadas

- Membresías vincula Usuarios y Talleres.
- Clientes pertenece a Talleres.
- Dispositivos representa equipos de Clientes y pertenece a Talleres.
- Órdenes de servicio registra visitas de Dispositivos.
- Tipos de dispositivos clasifica Dispositivos.
- Tipos de servicio cataloga servicios ofrecidos.
- Referencias provee Países/Monedas globales de solo lectura a Talleres.
- Proveedores ofrece selección opcional a entradas de Inventario.
- Inventario posee Repuestos/movimientos; Órdenes posee sus líneas snapshot.
- Pagos posee métodos y Pagos; una cuenta financiera por Orden coordina sus
  invariantes con total, entrega y anulaciones.
- Órdenes produce el DTO público; el adaptador PDF solo transforma ese DTO.

Las unidades transaccionales aceptadas coordinan Taller–dueño–Efectivo,
Orden–Repuesto–movimiento–historial y Orden–cuenta–Pago/anulación/entrega.
No son autorización para importar repositorios o documentos internos.

Diagnóstico, trabajo, garantía y entrega pertenecen a Órdenes. Notificaciones,
Auditoría general y Archivos no constituyen límites confirmados.
