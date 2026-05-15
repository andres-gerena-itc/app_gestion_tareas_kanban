# TECH_CONSTRAINTS.md — Restricciones Tecnológicas

Este documento fija los límites técnicos y convenciones de implementación. La IA debe ignorar cualquier solución que implique tecnologías fuera de este stack.

## 1. Stack Tecnológico Obligatorio
- **Lenguaje:** Python 3.11+ (Uso estricto de Type Hints).
- **Framework Web:** Flask 3.1.x (Como adaptador de entrada, sin lógica de negocio).
- **Persistencia:** Sistema de archivos local mediante `data/database.json`. 
  - *Prohibición:* No usar SQLite, PostgreSQL, Redis o cualquier base de datos externa.
- **Frontend:** Vanilla Web Stack (HTML5, CSS3 moderno, JavaScript ES6+).
  - *Prohibición:* No usar React, Vue, Angular, Tailwind o Bootstrap.
- **Pruebas:** Pytest para pruebas unitarias y de integración del backend.

## 2. Convenciones de Desarrollo
- **Idioma del Código:** Nombres de clases, métodos, variables y comentarios técnicos en **Inglés**.
- **Idioma de Interfaz:** Mensajes de error al usuario, etiquetas del tablero y documentación en **Español**.
- **Estilo:** Adherencia estricta a PEP 8.
- **Manejo de Datos:** Uso de `json` nativo de Python para la persistencia.

## 3. Restricciones de Dependencias
- No se permite el uso de ORMs (como SQLAlchemy).
- El dominio debe tener **Cero Dependencias** de librerías externas (excepto `uuid` o `datetime` nativos).
- No se permiten librerías de gestión de estado en frontend; usar el DOM y Fetch API de forma directa.