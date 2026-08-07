# Convenciones de API

## Estado

**Aceptado para fases 1 y 2:** API HTTP JSON con FastAPI bajo `/api/v1` y
OpenAPI generado. Los endpoints se registran por fase en `endpoints/`.

- Presentation traduce protocolo a casos de uso y no contiene reglas.
- Entradas se validan en el límite; invariantes se validan en Domain/Application.
- Respuestas no exponen documentos MongoDB ni excepciones internas.
- El contexto de identidad y Taller autorizado se construye del lado confiable.
- Operaciones deben tener semántica consistente de errores, paginación, filtros y versión.
- Contratos publicados requieren compatibilidad o una política de cambio explícita.

Los nombres de campos son `snake_case`. Las respuestas nunca exponen documentos
MongoDB. Compatibilidad más allá de `v1` queda pendiente.

Los importes son strings decimales, nunca números JSON de punto flotante. Los
endpoints públicos aceptan exclusivamente un token firmado en el path y no
requieren Bearer; todos los restantes mantienen autenticación y contexto.
