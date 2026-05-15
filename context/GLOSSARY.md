# GLOSSARY.md — Vocabulario Técnico Único

Para garantizar la consistencia en el código y las pruebas, se deben utilizar estrictamente estos términos:

| Término (Negocio) | Término en Código | Definición / Valores |
| :--- | :--- | :--- |
| **Tablero** | `Board` | El Aggregate Root que gestiona el conjunto de tareas. |
| **Tarea** | `Task` | Unidad mínima de trabajo. |
| **Identificador** | `id` | UUID generado para cada tarea. |
| **Título** | `title` | Cadena de texto que describe la tarea (Obligatorio). |
| **Estado** | `state` | El estado actual de la tarea en el flujo. |
| **Pendiente** | `TODO` | Estado inicial de una tarea creada. |
| **En Progreso** | `DOING` | Estado sujeto a la restricción de límite WIP. |
| **Terminado** | `DONE` | Estado final de la tarea. |
| **Límite WIP** | `WIP_LIMIT` | Constante numérica fija en **3** para el estado `DOING`. |
| **Repositorio** | `Repository` | Componente encargado de la persistencia de datos. |

## Mapeo de Errores de Dominio
- `WipLimitExceededError`: Error lanzado cuando se intenta mover a `DOING` superando el límite.
- `InvalidStateTransitionError`: Error lanzado si se intenta saltar estados (ej. de `TODO` a `DONE` directamente).