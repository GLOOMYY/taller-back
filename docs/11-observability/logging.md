# Logging operativo

## Estado propuesto

Logs estructurados con timestamp, severidad, evento, servicio/módulo y correlación. Contexto tenant/actor solo después de validarlo y cuando sea seguro.

No registrar secretos, credenciales, payloads completos, datos personales innecesarios ni trazas hacia clientes. Definir redacción y acceso antes de producción.

Formato, transporte, retención y consultas están **Pendientes**.
