# Health checks

## Contrato aceptado para fase 1

- **Liveness:** `GET /health/live` responde por el proceso sin consultar MongoDB.
- **Readiness:** `GET /health/ready` comprueba MongoDB e índices; responde `503`
  si la dependencia no está disponible.
- **Startup:** candidato si la inicialización lo necesita.

Las respuestas no exponen configuración, secretos ni topología. El comportamiento
de un orquestador de producción permanece fuera de alcance.
