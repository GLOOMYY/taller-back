# Seguimiento público y comprobantes

**Fase:** 2 · **Estado:** Aceptado

Órdenes posee la habilitación, versión y DTO público. Los endpoints autenticados
habilitan, rotan o revocan. El token no se almacena: codifica Orden y versión y
se autentica con HMAC. No se expone un ID de Orden sin firma ni se registra el
token. Rotar incrementa versión y revocar deshabilita la actual.

El DTO público contiene estado, equipo, falla, diagnóstico, trabajo, historial
operativo, servicios y Repuestos, y total final. Las líneas de servicio muestran
su nombre snapshot, incluido `Domicilio` cuando exista. Excluye precios
unitarios, métodos, Pagos/abonos, Proveedores, costos e historia financiera.

Comprobantes es un adaptador independiente: recibe únicamente ese DTO, no lee
colecciones ni es fuente de verdad. ReportLab genera el PDF mediante
`asyncio.to_thread`. JSON está disponible con token válido; PDF únicamente si
la Orden está `entregado`, por lo que una garantía lo oculta hasta nueva entrega.
El frontend público queda fuera.

Trazabilidad: BR-047; RF-SEG-001/002, RF-CMP-001; AC-037 a AC-040.

