# Gestor de Tareas Multidimensional (Arquitectura Limpia)

## 📖 Descripción del Proyecto

Este proyecto consiste en un avanzado sistema de gestión de tareas que evolucionó de un simple tablero Kanban con políticas de Límite WIP (Work In Progress) a convertirse en un potente motor de productividad. 

Basado firmemente en los principios de la **Arquitectura Limpia (Clean Architecture)**, **Arquitectura Hexagonal (Ports & Adapters)** y **CQRS (Proyecciones)**, el sistema orquesta reglas de negocio complejas de manera independiente a los frameworks e interfaces visuales. Combina la automatización de la matriz de Eisenhower con un motor de propiedades dinámicas inspirado en herramientas como Notion o Airtable.

## ✨ Características Clave

* **Tablero Kanban como Proyección (Vista de solo lectura):** El estado final del proyecto se expone utilizando un patrón CQRS, desvinculando la estructura de persistencia (Workspace/Project) de la interfaz de consumo visual. Soporta múltiples vistas (Kanban y Tabla) usando la misma fuente de verdad.
* **Invariantes de Dominio Protegidas:** Reglas de negocio inquebrantables, aseguradas desde la capa más profunda del código, como el Límite WIP (Máximo 3 tareas permitidas simultáneamente en la columna `DOING`).
* **Matriz de Eisenhower Automatizada:** El núcleo del sistema evalúa la urgencia e importancia de las tareas, determinando automáticamente a qué cuadrante pertenecen (Hacer, Planificar, Delegar o Eliminar).
* **Gestión de Jerarquías (Subtareas):** Lógica robusta que previene ciclos infinitos de dependencia (una tarea padre no puede ser hija de su propia subtarea) y establece límites de profundidad controlados.
* **Motor de Validación para Propiedades Dinámicas (Custom Fields):** El usuario final puede crear esquemas de propiedades al vuelo (Texto, Número, Fecha, Booleano). El dominio de la aplicación valida estrictamente estos tipos de datos antes de cualquier persistencia.

## 🛠️ Stack Tecnológico

* **Backend / Dominio:** Python 3.14 (Uso intensivo de Dataclasses, Type Hinting y Enums).
* **Infraestructura (Adaptador HTTP):** Flask.
* **Frontend:** Vanilla JavaScript y HTML/CSS puro (Uso de CSS Grid/Flexbox y DOM manipulation nativa).
* **Persistencia:** Repositorio basado en JSON, asegurando fácil portabilidad y cero dependencias de motores SQL en esta iteración.
* **Testing:** Pytest para TDD (Test-Driven Development) y validación de Invariantes de Dominio.

## 🚀 Instrucciones de Instalación y Ejecución

Para desplegar este proyecto en un entorno local, sigue las instrucciones de la terminal (Windows PowerShell / Linux Bash):

1. **Clonar el repositorio y ubicarse en la raíz del proyecto:**
   Asegúrate de estar en el directorio `app_gestion_tareas_kanban`.

2. **Crear y activar el entorno virtual (venv):**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar las dependencias del proyecto:**
   ```bash
   pip install flask pytest
   ```

4. **Levantar el Servidor de Desarrollo Flask:**
   ```bash
   python -m src.infrastructure.flask_app
   ```
   *El servidor se iniciará en `http://127.0.0.1:5000/`. Abre este enlace en tu navegador web para utilizar la aplicación.*

## 🧪 Instrucciones de Pruebas

El sistema cuenta con una robusta suite de pruebas unitarias enfocada en validar la integridad de la Capa de Dominio (validaciones WIP, transiciones de estado, límites jerárquicos).

Para ejecutar todos los tests, asegúrate de tener tu entorno virtual activo y ejecuta:
```bash
pytest tests/
```
Para ver un reporte detallado (Verbose):
```bash
pytest tests/ -v
```

---
*Diseñado bajo estándares de ingeniería de software con enfoque en el Dominio (DDD - Domain Driven Design).*