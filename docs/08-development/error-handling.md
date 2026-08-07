# Manejo de errores

## Propuesta obligatoria al implementar

- Domain expresa violaciones de reglas con errores propios independientes del protocolo.
- Application distingue fallos esperados, autorización y fallos externos.
- Infrastructure traduce fallos de tecnología sin filtrar detalles al núcleo.
- Presentation convierte errores conocidos al contrato público y asigna correlación.
- Nunca silenciar un error ni usarlo como flujo normal si existe una alternativa clara.
- No registrar el mismo error repetidamente en cada capa.

Jerarquía concreta, reintentos, idempotencia y mensajes públicos están **Pendientes**.
