# Principios del proyecto

## Aceptados

1. **Aislamiento primero.** Toda operación y dato operativo se limita al Taller del contexto autorizado.
2. **KISS.** Elegir la solución más simple que cumpla requisitos confirmados.
3. **YAGNI.** No implementar flexibilidad, módulos o reglas anticipadas.
4. **SOLID con criterio.** Usar sus principios para reducir acoplamiento, sin multiplicar capas o interfaces sin necesidad.
5. **Clean Code.** Nombres claros, unidades pequeñas con responsabilidad coherente, errores explícitos y mínima duplicación significativa.
6. **Dominio independiente.** El dominio no depende de MongoDB, frameworks web ni detalles de presentación.
7. **Módulos con límites.** La colaboración ocurre mediante contratos explícitos, no accediendo a internals o almacenamiento ajeno.
8. **Documentar incertidumbre.** Una inferencia se marca Propuesta, Candidata o Pendiente.
9. **Pruebas proporcionales al riesgo.** En especial tenancy, reglas de dominio, límites arquitectónicos y persistencia.
10. **Trazabilidad.** Requisitos, reglas, aceptación y cambios deben poder relacionarse por identificadores.

## Precedencia normativa para Python

Cuando exista conflicto: **reglas documentadas del proyecto > Google Python Style Guide > PEP 8**. PEP 257 rige docstrings y los type hints son obligatorios en código futuro sujeto a las excepciones explícitas que el proyecto llegue a aprobar.
