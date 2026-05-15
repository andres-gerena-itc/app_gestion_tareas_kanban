# FEATURE_SPEC_002: Mover Tarea (Flujo y Límite WIP)

## 1. Descripción
Define las reglas para transicionar una tarea (`Task`) existente entre los diferentes estados del tablero Kanban, protegiendo el flujo de trabajo y la capacidad máxima de atención del usuario (WIP Limit).

## 2. Precondiciones
- El `Board` debe existir y contener al menos una tarea previamente creada.

## 3. Entradas
- `id` (UUID string): El identificador de la tarea a mover.
- `target_state` (Enum/String): El estado al que se desea mover la tarea (`TODO`, `DOING`, `DONE`).

## 4. Reglas de Negocio
- **R1 - Flujo Secuencial:** Las transiciones de estado permitidas son estrictamente:
  - `TODO` -> `DOING`
  - `DOING` -> `DONE`
- **R2 - Límite WIP (Work In Progress):** El sistema no puede tener más de `WIP_LIMIT` (3) tareas en estado `DOING` simultáneamente.
- **R3 - Existencia:** La tarea solicitada debe existir en el tablero.

## 5. Flujo Principal (Camino Feliz)
1. El cliente solicita mover la tarea con `id` hacia el `target_state`.
2. El sistema recupera el `Board` y busca la tarea.
3. El sistema valida que la transición cumpla con R1.
4. Si `target_state` es `DOING`, el sistema cuenta las tareas actuales en ese estado para verificar R2.
5. El sistema actualiza el estado de la tarea.
6. El sistema guarda el estado del tablero a través del Repositorio.
7. El sistema retorna confirmación de éxito.

## 6. Flujos Alternativos / Errores
- **E1 - Tarea Inexistente:** Si el `id` no se encuentra, lanzar `TaskNotFoundError`.
- **E2 - Transición Inválida:** Si se intenta un salto no permitido (ej. de `TODO` directamente a `DONE`), lanzar `InvalidStateTransitionError`.
- **E3 - Límite WIP Excedido:** Si el destino es `DOING` y ya existen 3 tareas en ese estado, rechazar la operación y lanzar `WipLimitExceededError`. El tablero queda intacto.

## 7. Criterios de Aceptación (Para Pruebas Automatizadas)
- **AC-02.01:** Dada una tarea en `TODO` y 0 tareas en `DOING`, cuando se mueve la tarea a `DOING`, entonces su estado se actualiza exitosamente.
- **AC-02.02:** Dada una tarea en `DOING`, cuando se mueve a `DONE`, entonces su estado se actualiza exitosamente.
- **AC-02.03:** Dada una tarea en `TODO` y 3 tareas ya existentes en `DOING`, cuando se intenta mover la tarea a `DOING`, entonces se lanza `WipLimitExceededError` y la tarea original permanece en `TODO`.
- **AC-02.04:** Dada una tarea en `TODO`, cuando se intenta mover directamente a `DONE`, entonces se lanza `InvalidStateTransitionError`.