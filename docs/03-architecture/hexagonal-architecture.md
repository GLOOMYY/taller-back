# Arquitectura hexagonal

## Regla aceptada

El núcleo expresa negocio sin depender de tecnologías externas. Las interacciones entran por puertos de entrada y los casos de uso solicitan capacidades externas mediante puertos de salida.

## Responsabilidades

### Domain

Entidades, value objects candidatos, invariantes, servicios de dominio cuando sean necesarios y errores de dominio. No conoce HTTP, MongoDB ni configuración.

### Application

Casos de uso, coordinación transaccional o de consistencia cuando aplique, validación del contexto autorizado y contratos de salida. No contiene detalles de drivers.

### Infrastructure

Repositorios MongoDB, proveedores de identidad, reloj, identificadores u otras integraciones futuras. Implementa puertos definidos hacia el núcleo.

### Presentation

Traduce solicitudes y respuestas del canal al lenguaje de aplicación. No contiene reglas de negocio ni accede directamente a MongoDB.

## Prueba de diseño

Una regla de dominio debe poder probarse sin servidor, base de datos ni framework. Un adaptador debe poder reemplazarse sin modificar esa regla.
