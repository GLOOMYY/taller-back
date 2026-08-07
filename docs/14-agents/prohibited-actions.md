# Acciones prohibidas

- Inventar o promover requisitos, reglas, campos, estados, roles, permisos, endpoints o módulos sin aceptación.
- Implementar fases futuras o candidatos “por si acaso”.
- Confiar solo en `taller_id` del cliente o ejecutar consultas operativas sin scope tenant.
- Compartir Clientes o datos operativos entre Talleres por conveniencia técnica.
- Acceder directamente a MongoDB desde Domain/Presentation o a colecciones de otro módulo.
- Crear ciclos de dependencia o importar internals de módulos.
- Convertir Reportes en fuente canónica.
- Introducir microservicios, buses, frameworks, repositorios genéricos o abstracciones sin necesidad vigente.
- Ocultar errores, capturar excepciones indiscriminadamente o exponer trazas/detalles internos.
- Guardar o imprimir secretos, tokens, credenciales o datos sensibles innecesarios.
- Debilitar/eliminar pruebas para hacer pasar un cambio.
- Modificar archivos o refactorizar módulos fuera del alcance sin necesidad y autorización.
- Fijar esquemas MongoDB por analogía relacional antes de agregados y consultas.
- Declarar verificaciones no ejecutadas o cambiar silenciosamente el estado de Pendiente a Aceptado.
