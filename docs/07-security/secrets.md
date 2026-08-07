# Secretos

## Reglas aceptadas

- Nunca guardar secretos en código, repositorio, documentación, imágenes, fixtures o logs.
- Inyectarlos mediante configuración segura por entorno cuando se elija el mecanismo.
- Limitar acceso y alcance; separar por entorno.
- Rotar y revocar sin cambiar código.
- Redactar tokens, credenciales y datos sensibles de errores y observabilidad.

Gestor de secretos, rotación, responsables y respuesta a exposición están **Pendientes**. Los archivos locales de entorno no se consideran almacenamiento seguro para producción.

## Seguimiento público de fase 2

La clave HMAC es configuración secreta obligatoria, separada por entorno y no
reutilizada como credencial OIDC. Los tokens firmados no se persisten ni se
incluyen en logs, errores, métricas o correlación. Rotación de enlace incrementa
la versión de Orden; rotación del secreto de infraestructura requiere una
operación explícita y puede invalidar enlaces existentes.
