# Docker

## Estado de fase 1

Docker Compose está **Aceptado** para el MongoDB local reproducible con replica
set de un nodo. La API se ejecuta con Python/Uvicorn fuera del contenedor.

Si se adopta: imagen reproducible, mínima, sin secretos, usuario no privilegiado, dependencias fijadas, health check coherente y separación entre build/runtime cuando aporte valor. El contenedor no almacena estado persistente de MongoDB local en producción.

Imágenes base, registry, orquestador y estrategia de build están **Pendientes**.
