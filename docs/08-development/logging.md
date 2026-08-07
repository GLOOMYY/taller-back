# Logging para desarrollo

## Propuesta

- Logs estructurados y orientados a eventos, no frases ambiguas.
- Incluir correlación y, cuando sea seguro, identificador interno de Taller/actor; nunca confiar en valores no validados.
- Registrar en límites útiles y evitar duplicación entre capas.
- Excluir secretos, tokens, payloads completos y datos personales no necesarios.
- Usar niveles de forma consistente y no convertir sucesos esperados en errores.

Formato, librería y política de campos están **Pendientes**. Véase `11-observability/logging.md`.
