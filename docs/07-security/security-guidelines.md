# Guías de seguridad

## Aceptadas

- Validar entrada en límites y reglas en el núcleo correspondiente.
- Usar consultas seguras; no aceptar operadores MongoDB arbitrarios desde clientes.
- Aplicar mínimo privilegio a identidades y conexiones.
- No exponer trazas, detalles internos, secretos o existencia cross-tenant.
- Mantener dependencias controladas y revisar vulnerabilidades antes de producción.
- Proteger datos en tránsito y almacenamiento según decisiones futuras.
- Tratar autorización tenant como regla transversal, no middleware único suficiente.

## Pendiente

Clasificación de datos, cifrado concreto, retención, cumplimiento regulatorio, rate limiting, CORS/CSRF, cabeceras, respuesta a incidentes y threat model detallado.
