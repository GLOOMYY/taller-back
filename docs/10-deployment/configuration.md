# Configuración

## Reglas aceptadas

- Configuración externa al código y validada al iniciar.
- Valores por entorno explícitos; secretos separados de configuración no sensible.
- Fallar de forma clara ante configuración obligatoria ausente o inválida.
- No usar valores por defecto inseguros en producción.
- Documentar cada variable sin incluir su valor secreto.

`pydantic-settings` valida variables con prefijo `TALLER_` y puede leer `.env`
solo para desarrollo local. `.env.example` documenta el esquema sin secretos.

Fase 2 añade una clave HMAC obligatoria para seguimiento público. La
configuración valida presencia/fortaleza al iniciar y nunca incluye el valor en
errores o logs. ReportLab no recibe acceso a configuración ni persistencia.
