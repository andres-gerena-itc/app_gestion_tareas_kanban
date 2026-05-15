# DOMAIN.md — Bounded Context *Task Management*

> **Archivo de paquete de contexto (2 de 5).** Este documento define el vocabulario compartido del dominio, los aggregates, las invariantes inviolables y los eventos de dominio. Es la fuente de verdad para cualquier regla de negocio discutida en especificaciones, código o pruebas.

---

## 1. Lenguaje Ubicuo

Toda interacción humana o algorítmica con el sistema debe emplear estrictamente los siguientes términos con su significado exacto. El uso de sinónimos o traducciones libres está prohibido en código, especificaciones, nombres de tablas, endpoints y mensajes.

| Término             | Definición                                                                                                                                   |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `Workspace`         | Contenedor raíz del usuario; agrupa `Projects` y `PropertySchemas`. Identificado por `workspaceId`.                                          |
| `Project`           | Contenedor de `Tasks` dentro de un Workspace. Un Project tiene muchas Tasks; una Task pertenece a exactamente un Project. Aggregate root.    |
| `Task`              | Unidad de trabajo identificable. Aggregate root. Contiene sus `PropertyValues` y referencias a sus subtareas.                                |
| `Subtask`           | Una `Task` cuyo `parentTaskId` referencia a otra Task del mismo Project.                                                                     |
| `Urgency`           | Atributo booleano de Task. `true` cuando la Task requiere atención inmediata (hoy / esta semana).                                            |
| `Importance`        | Atributo booleano de Task. `true` cuando la Task tiene impacto estratégico sobre los objetivos del usuario.                                  |
| `Quadrant`          | Valor **derivado** de `(Urgency, Importance)`. Uno de: `HACER`, `PLANIFICAR`, `DELEGAR`, `ELIMINAR`. No se persiste jamás.                   |
| `PropertySchema`    | Definición de una propiedad dinámica disponible en un Workspace: `{ name, type, config }`.                                                   |
| `PropertyValue`     | Valor concreto asignado a una `PropertySchema` sobre una Task específica. Debe satisfacer el tipo declarado.                                 |
| `PropertyType`      | Uno de seis tipos soportados: `Status`, `Select`, `MultiSelect`, `Date`, `Formula`, `Relation`.                                              |
| `View`              | Proyección de solo lectura sobre un conjunto de Tasks. Uno de: `TableView`, `KanbanView`, `CalendarView`.                                    |
| `Archived Task`     | Una Task cuyo campo `archivedAt` es distinto de `null`. Sigue existiendo pero no aparece en las vistas por defecto.                          |

## 2. Aggregate Roots

El dominio tiene tres aggregate roots. Cada uno es la única puerta de escritura a las entidades que contiene, y cualquier transacción escribe exactamente un aggregate a la vez.

### 2.1 Workspace
Raíz de consistencia de la **estructura dinámica** del sistema. Contiene:
- Una colección de `PropertySchemas`.
- La configuración del Workspace (nombre, tz por defecto).

No contiene Tasks ni Projects directamente: los referencia por ID para evitar aggregates gigantes.

### 2.2 Project
Raíz de consistencia de la **agrupación de Tasks**. Contiene:
- `projectId`, `workspaceId`, `name`, `createdAt`.
- Una referencia lógica a sus Tasks (por ID, no por composición).

No navega a las Tasks: son agregado distinto. Eliminar un Project con Tasks activas está prohibido (ver `INV-07`).

### 2.3 Task
Raíz de consistencia de la **unidad de trabajo**. Contiene:
- Identidad, atributos intrínsecos (`title`, `urgency`, `importance`, `dueDate`, `archivedAt`).
- Referencias: `projectId`, `parentTaskId?`.
- Un mapa de `PropertyValues` serializable como `JSONB`.
- Su `Quadrant` expuesto como atributo calculado, nunca almacenado.

Las subtareas se modelan por referencia (`parentTaskId`), no por composición, para permitir edición independiente y consultas eficientes sobre el árbol.

## 3. Invariantes del Dominio (inviolables)

Las invariantes siguientes deben cumplirse en todo momento. Cualquier estado que las viole es un *bug de contrato* y debe ser rechazado por el aggregate correspondiente.

- **INV-01** — **Quadrant no persistido**: el `Quadrant` de una Task NUNCA se almacena como atributo persistente. Se calcula en cada lectura a partir de `(urgency, importance)`. Cualquier columna llamada `quadrant` en la base de datos viola este contrato.

- **INV-02** — **Regla de derivación del Quadrant**:
  - `(urgency = true,  importance = true)`  → `HACER`
  - `(urgency = false, importance = true)`  → `PLANIFICAR`
  - `(urgency = true,  importance = false)` → `DELEGAR`
  - `(urgency = false, importance = false)` → `ELIMINAR`

- **INV-03** — **Profundidad de subtareas**: el árbol de subtareas no puede exceder 3 niveles. Formalmente: para toda Task `t`, `depth(t) ≤ 3`, donde `depth(root) = 1`.

- **INV-04** — **Ausencia de ciclos**: ninguna Task puede ser ancestra de sí misma. Reasignar `parentTaskId` a un descendiente directo o transitivo es una operación prohibida.

- **INV-05** — **Cardinalidad Project-Task**: toda Task pertenece a exactamente un Project. `projectId` es obligatorio y no nulo.

- **INV-06** — **Tipado de PropertyValue**: para toda Task `t` con un `PropertyValue v` bajo la clave `k`, existe en el Workspace un `PropertySchema s` con `s.name = k`, y el valor `v` satisface el tipo declarado por `s.type`. Un valor que no puede validarse contra su schema es rechazado en escritura.

- **INV-07** — **Eliminación protegida de Project**: un Project con al menos una Task no archivada no puede ser eliminado. El aggregate Project rechaza la operación `delete()` si `countActiveTasks() > 0`.

- **INV-08** — **Views son solo lectura**: las proyecciones `TableView`, `KanbanView`, `CalendarView` no introducen estado adicional en el dominio, no tienen su propia tabla y no aceptan operaciones de escritura. Son composiciones en memoria a partir del estado de las Tasks.

- **INV-09** — **Coherencia subtarea-proyecto**: si una Task es subtarea, su `projectId` debe coincidir con el `projectId` de su Task padre. La regla se evalúa en la creación y en cada operación `moveToProject()`.

- **INV-10** — **Inmutabilidad de identificadores**: los identificadores (`workspaceId`, `projectId`, `taskId`, `propertySchemaId`) son inmutables una vez creados. No hay operación `rename` a nivel de identidad.

## 4. Tipos de PropertySchema soportados

El sistema soporta exactamente los seis tipos siguientes. Añadir un séptimo requiere actualizar este archivo, no inferirlo. El esquema detallado de cada tipo vive en `specs/CONTRACTS/domain_schemas.json`.

- **`Status`**: enumeración de estados fijos con un estado por defecto. Ejemplo: `["Todo", "InProgress", "Done"]` con default `"Todo"`.
- **`Select`**: selección única de una lista configurable de opciones etiquetadas con color.
- **`MultiSelect`**: selección múltiple sobre la misma estructura de opciones.
- **`Date`**: fecha con o sin hora, siempre almacenada en UTC.
- **`Formula`**: expresión evaluable que produce un valor derivado a partir de otras propiedades de la misma Task. La evaluación es pura: sin efectos laterales, sin E/S, sin referencias a otras Tasks.
- **`Relation`**: referencia a otra entidad del mismo Workspace (inicialmente solo `Project`; otros destinos quedan fuera del laboratorio).

## 5. Eventos de Dominio

El dominio publica eventos inmutables tras cada operación de escritura exitosa. Cada evento transporta `correlationId: uuid`, `occurredAt: ISO-8601` y la mínima información contextual necesaria.

- `TaskCreated(taskId, projectId, title, urgency, importance, createdAt)`
- `TaskClassified(taskId, quadrant)` — emitido tras `TaskCreated` y tras cualquier cambio que altere `(urgency, importance)`.
- `TaskTitleChanged(taskId, oldTitle, newTitle)`
- `TaskMovedToProject(taskId, oldProjectId, newProjectId)`
- `SubtaskAttached(parentTaskId, childTaskId)`
- `SubtaskDetached(parentTaskId, childTaskId)`
- `PropertyValueChanged(taskId, propertyName, oldValue, newValue)`
- `TaskArchived(taskId, archivedAt)`
- `TaskUnarchived(taskId)`
- `PropertySchemaAdded(workspaceId, schemaName, schemaType)`
- `PropertySchemaRemoved(workspaceId, schemaName)`

Los eventos NO cruzan la frontera de este contexto. Su consumidor principal es el mecanismo de auditoría y, opcionalmente, un *event store* local. No se publican en un bus externo.

## 6. Reglas de negocio explícitas adicionales

Además de las invariantes, aplican las siguientes reglas operativas:

- **Herencia de Project en subtareas**: al crear una subtarea, si no se especifica `projectId`, se hereda del padre. Si se especifica uno distinto al del padre, la creación se rechaza (no se "corrige"). Ver `INV-09`.
- **Archivar vs eliminar**: archivar es reversible (`archivedAt` puede volver a `null`). Eliminar es irreversible y solo permitido en Tasks archivadas sin subtareas activas.
- **Cambio de Urgency/Importance**: recalcula el Quadrant y dispara `TaskClassified` solo si el Quadrant resultante es distinto del anterior.
- **Formula determinista**: el evaluador de `Formula` es puro; dos evaluaciones sobre la misma Task con el mismo estado producen el mismo resultado.

## 7. Relaciones entre invariantes y eventos

La tabla siguiente traza qué eventos deben verificarse contra qué invariantes durante su generación. Es referencia útil tanto para tests como para revisiones de código generado por IA.

| Evento                      | Invariantes a verificar antes de emitir     |
|-----------------------------|---------------------------------------------|
| `TaskCreated`               | INV-02, INV-03, INV-05, INV-06, INV-09      |
| `TaskClassified`            | INV-01, INV-02                              |
| `SubtaskAttached`           | INV-03, INV-04, INV-09                      |
| `TaskMovedToProject`        | INV-05, INV-09                              |
| `PropertyValueChanged`      | INV-06                                      |
| `PropertySchemaRemoved`     | INV-06 (rechazar si existen PropertyValues) |

---

*Este archivo es parte del paquete de contexto del Bounded Context **Task Management**. Cualquier modificación estructural —adición o cambio de invariantes, tipos o aggregates— requiere commit atómico cuyo mensaje comience por `docs(context): invariantes` o `docs(context): tipos` según corresponda.*
