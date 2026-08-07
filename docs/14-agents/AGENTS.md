# Instrucciones obligatorias para agentes

## Antes de tocar código

1. Leer `docs/README.md` y todo `docs/00-overview/`.
2. Leer reglas y requisitos relevantes en `01-business/` y `02-requirements/`.
3. Leer `03-architecture/`, el archivo del módulo en `04-domain/` y los ADR vigentes.
4. Leer las guías de datos, seguridad, desarrollo y pruebas aplicables.
5. Confirmar que la tarea cumple Definition of Ready.

## Reglas de ejecución

- No inventar requisitos, estados, campos, endpoints, roles, permisos, procesos o integraciones.
- Tratar solo **Aceptado/Confirmado** como obligatorio. Propuesto, Candidato y Pendiente requieren decisión antes de implementación.
- No modificar otros módulos salvo necesidad demostrable y dentro del alcance de la tarea.
- No introducir dependencias, patrones, capas o abstracciones sin justificar una necesidad actual.
- Preferir la solución más simple que cumpla requisitos y seguridad.
- Respetar monolito modular, arquitectura hexagonal, puertos/adaptadores y dirección de dependencias.
- Preservar aislamiento tenant en cada entrada, caso de uso, referencia, repositorio, consulta y prueba.
- Nunca confiar únicamente en un `taller_id` enviado por el cliente; validar identidad, Membresía/contexto y pertenencia.
- No acceder a internals o colecciones de otro módulo.
- Mantener nombres de dominio en español.
- Cumplir PEP 8, PEP 257, Google Python Style Guide, type hints y la precedencia del proyecto.
- Incluir pruebas proporcionales y actualizar documentación afectada.
- No sobrearquitecturar ni preparar fases futuras sin autorización.

## Ante ambigüedad

Buscar primero en esta documentación. Si la decisión no existe y cambia comportamiento o contrato, registrar/elevar la pregunta; no asumir. Una observación de diseño puede marcarse Propuesta sin convertirla en requisito.

## Protección del trabajo existente

No revertir cambios ajenos, no hacer refactorizaciones fuera de alcance, no añadir secretos y no declarar completado sin ejecutar las verificaciones pertinentes.
