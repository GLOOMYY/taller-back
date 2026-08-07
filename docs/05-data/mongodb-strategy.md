# Estrategia MongoDB

## Decisión aceptada para fases 1 y 2

MongoDB es la persistencia y se usa una base compartida con colecciones
compartidas. Los documentos operativos incluyen `taller_id` y toda consulta
operativa se limita por el `ContextoTaller` autorizado.

El driver es **PyMongo 4.13.2** mediante su API asíncrona nativa
`AsyncMongoClient`; no se usa ODM. Domain y Application permanecen
independientes de PyMongo. Las instancias de cliente y base se crean en el
ciclo de vida de la aplicación y se inyectan en adaptadores concretos.

## Identificadores

Clientes usa `ObjectId` generado por MongoDB; Usuarios, Talleres y Membresías
usan UUID serializado. Solo los adaptadores conocen esos formatos: todos cruzan
los puertos y la API como `str` opacos. Un identificador mal formado se trata
como recurso no encontrado, sin filtrar detalles técnicos.

## Consistencia y transacciones

- Las operaciones de un único documento, como crear o editar un Cliente, usan
  la atomicidad nativa de MongoDB y no abren transacción.
- Crear un Taller y su Membresía inicial de dueño es una sola operación de
  negocio sobre dos colecciones. Se ejecuta en una sesión y transacción MongoDB;
  ambos documentos se confirman o ninguno queda visible (RF-TAL-001, AC-017).
- El entorno local usa un replica set de un nodo porque MongoDB exige replica
  set o clúster fragmentado para transacciones multi-documento.
- Fase 2 compone unidades de trabajo para Taller–dueño–Efectivo;
  Orden–Repuesto–movimiento–historial; cambios de total frente a lo pagado;
  Pago/anulación–cuenta–historial; y entrega/reapertura–cuenta–historial.
- La cuenta financiera de Orden es el documento bloqueado/modificado dentro de
  la transacción para serializar mutaciones concurrentes y volver a comprobar
  total, pagado y saldo antes del commit.
- Consecutivos usan un documento contador por Taller y `$inc` atómico.

Read concern, write concern, reintentos y política de transacciones para
producción quedan fuera de esta fase local y deben decidirse antes de desplegar.

## Método de modelado

1. Partir de agregados y casos de uso aceptados.
2. Registrar los patrones de consulta y la clave tenant.
3. Preferir una operación atómica de documento cuando basta.
4. Justificar referencias, transacciones e índices por una necesidad actual.
5. Verificar con MongoDB real, al menos dos Talleres e identificadores cruzados.
