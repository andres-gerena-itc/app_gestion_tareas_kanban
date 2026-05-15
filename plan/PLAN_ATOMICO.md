# PLAN_ATOMICO.md — Ruta de Implementación

> **Nota para la IA:** Este archivo documenta el plan paso a paso. Cada paso debe ser atómico, reversible (un solo `git revert`) y enfocado en una sola capa a la vez. No se debe avanzar al siguiente paso sin la aprobación explícita del usuario.

## Estado de Ejecución
- [x] **Paso 1:** Configuración inicial del proyecto y estructura de carpetas.
  - 1.1 Crear estructura de directorios: `src/domain/`, `src/application/`, `src/infrastructure/`, `data/`, y `tests/`.
  - 1.2 Crear archivos `__init__.py` para definir los paquetes de Python.
- [x] **Paso 2:** Implementación del Dominio (Entidades `Task`, `Board` y Límite WIP).
  - 2.1 Definir excepciones de dominio (`InvalidTitleError`, `TaskNotFoundError`, `InvalidStateTransitionError`, `WipLimitExceededError`) en `src/domain/exceptions.py`.
  - 2.2 Crear entidad `Task` (`id` UUID, `title` string, `state` Enum/string) en `src/domain/task.py` aplicando la regla de negocio de Título Obligatorio y Estado Inicial `TODO`.
  - 2.3 Crear agregado `Board` en `src/domain/board.py` que valide el límite de WIP (máx 3 en `DOING`) y controle las transiciones válidas (`TODO` -> `DOING` -> `DONE`).
- [x] **Paso 3:** Pruebas unitarias del Dominio (Validación de WIP).
- [x] **Paso 4:** Implementación de Casos de Uso (Capa de Aplicación).
  - 4.1 Definir el puerto de persistencia (interfaz `RepositoryInterface`) en `src/application/repository.py`.
  - 4.2 Implementar `CreateTaskUseCase` para orquestar la validación y el guardado.
  - 4.3 Implementar `MoveTaskUseCase` para orquestar el movimiento y aplicar el límite WIP mediante el dominio.
  - 4.4 Implementar `GetBoardUseCase` para retornar el estado general sin alterar datos.
- [x] **Paso 5:** Implementación del Repositorio JSON (Infraestructura).
- [x] **Paso 6:** Implementación del servidor Flask y endpoints HTTP (Infraestructura).
- [x] **Paso 7:** Construcción del Frontend Vanilla JS.
- [ ] **Paso 8:** Pruebas de integración manuales y ajustes finales.

## FASE 2: Expansión Multidimensional (Notion-like)

- [ ] **Paso 9: Rediseño del Dominio Central**
  - 9.1 Refactorizar agregados: Crear `Workspace` y `Project` (INV-05).
- [ ] **Paso 10: Clasificación Eisenhower**
  - 10.1 Añadir atributos `urgency` e `importance` a `Task`.
  - 10.2 Implementar derivación de `Quadrant` en memoria sin persistir (INV-01, INV-02).
- [ ] **Paso 11: Jerarquía de Tareas (Subtasks)**
  - 11.1 Añadir `parentTaskId` a `Task`.
  - 11.2 Implementar validaciones contra ciclos (INV-04) y profundidad máxima (INV-03).
- [ ] **Paso 12: Propiedades Dinámicas**
  - 12.1 Definir `PropertySchema` en `Workspace` (6 tipos nativos).
  - 12.2 Validar que los `PropertyValues` de una `Task` coincidan estrictamente con el esquema (INV-06).
- [ ] **Paso 13: Proyecciones e Infraestructura**
  - 13.1 Tratar el tablero Kanban como una `View` calculada (solo lectura), descontinuando el agregado monolítico actual (INV-08).
  - 13.2 Actualizar el adaptador JSON para soportar persistencia desde la raíz del `Workspace`.

*(El detalle de cada paso será completado durante la fase de ejecución)*