# ADR-009: Seguimiento público y comprobantes

- **Estado:** Aceptado
- **Fecha:** 2026-08-07

## Contexto

Un cliente sin cuenta debe consultar el avance y, al entregar, un comprobante.
Un ID opaco solo no es autorización. El enlace debe ser permanente, revocable y
rotatable, sin almacenar ni filtrar tokens ni exponer detalles financieros o de
abastecimiento.

## Decisión

Órdenes guarda habilitación y versión de seguimiento. El enlace porta un token
firmado con HMAC sobre identidad de Orden y versión. El secreto proviene de
configuración segura. No se persiste ni registra el token. Revocar deshabilita;
rotar incrementa versión, invalidando enlaces anteriores. No expira por tiempo:
permanece válido hasta una de esas acciones.

El caso de uso de Órdenes produce un DTO público limitado: estado, equipo,
falla, diagnóstico, trabajo, historial operativo, servicios/Repuestos sin
precios unitarios y total final. Excluye métodos, Pagos, Proveedores, costos y
un ID de Orden sin firma.

Comprobantes es un adaptador de salida independiente. Recibe exclusivamente el
DTO, no consulta colecciones y no es fuente de verdad. ReportLab genera bytes
PDF mediante `asyncio.to_thread`. El PDF solo se sirve si la Orden está
`entregado`; una reapertura lo oculta hasta nueva entrega. JSON sigue disponible
con el estado vigente. El frontend imprimible no forma parte de fase 2.

## Alternativas descartadas

- ID de Orden o token aleatorio persistido: el primero no autoriza; el segundo
  añade almacenamiento de secretos sin necesidad.
- JWT con expiración: contradice el enlace permanente hasta revocación/rotación.
- PDF leyendo repositorios: rompe límites y podría divergir del DTO público.
- Generar ReportLab directamente en el event loop: bloquearía la API async.

## Consecuencias

- HMAC exige secreto separado por entorno y rotación operativa explícita.
- Respuestas inválidas/no disponibles usan `404` sin oráculo de existencia.
- Pruebas cubren alteración, versión, revocación, filtrado y render visual.
- Trazabilidad: BR-047; RF-SEG-001/002, RF-CMP-001; AC-037 a AC-040; RNF-012.

