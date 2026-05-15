# CONTEXT.md — Gestor de Tareas Multidimensional

> **Archivo de paquete de contexto (1 de 5).** Este documento describe el *qué* y el *para quién* del sistema desde la perspectiva de producto. Es la primera lectura obligatoria para cualquier persona —o modelo de lenguaje— que vaya a intervenir en este Bounded Context.

---

## 1. Propósito

Proveer a los usuarios un sistema de gestión de tareas que combina la **clasificación Eisenhower** (matriz de urgencia × importancia) con un **sistema de propiedades dinámicas al estilo Notion** y **múltiples vistas** (Tabla, Kanban, Calendario) operando sobre un único modelo de dominio, sin duplicación de datos entre vistas.

El sistema debe permitir al usuario priorizar su trabajo con una regla explícita (el cuadrante Eisenhower se calcula automáticamente), extender el esquema de cada tarea con propiedades personalizadas definidas a nivel de Workspace, y consumir la información en la vista más adecuada al momento del día: Tabla para edición masiva, Kanban para gestión visual del flujo, Calendario para planificación temporal.

## 2. Stakeholders

- **Usuario individual**: gestiona su propio conjunto de tareas personales dentro de un Workspace privado. Es el actor principal del sistema.
- **Usuario de equipo**: organiza tareas dentro de un Project compartido, coordinando su trabajo con pares. Nota: el laboratorio no aborda permisos multi-usuario; se asume que el usuario autenticado tiene acceso completo al Workspace.
- **Administrador de Workspace**: define y evoluciona los `PropertySchemas` que estarán disponibles para todas las tareas del Workspace. Es el único actor que puede modificar la estructura dinámica.
- **Ingeniero de contexto (estudiante)**: responsable de mantener este paquete de contexto y las especificaciones como la fuente de verdad del sistema.

## 3. Métricas de éxito

El sistema se considera funcional cuando cumple los siguientes umbrales operativos:

- **Latencia de escritura**: crear una Task responde en menos de 200 ms (p95), incluyendo el cálculo del cuadrante Eisenhower y la validación de `PropertyValues`.
- **Consistencia del cuadrante**: el cuadrante observado coincide con el esperado en el 100 % de los casos; no existe camino de código en el que una Task pueda exponer un cuadrante distinto al derivado de `(urgency, importance)`.
- **Cambio de vista**: alternar entre Tabla, Kanban y Calendario es una operación de proyección en memoria y no dispara nuevas lecturas a la base de datos cuando el conjunto de tareas ya está cargado.
- **Trazabilidad**: toda operación de escritura emite al menos un evento de dominio con `correlationId` y `timestamp`.

## 4. Alcance EN este Bounded Context

El Bounded Context **Task Management** atiende exclusivamente las siguientes capacidades:

- Crear, editar, eliminar y archivar `Tasks`.
- Mover `Tasks` entre `Projects` dentro del mismo Workspace.
- Definir y modificar `PropertySchemas` a nivel de Workspace.
- Asignar y modificar `PropertyValues` de una Task dentro de los tipos permitidos.
- Soporte para subtareas hasta una profundidad máxima de 3 niveles (raíz, hijo, nieto).
- Relación muchos-a-uno entre `Task` y `Project`.
- Cálculo automático del cuadrante Eisenhower a partir de `(urgency, importance)`.
- Proyecciones de lectura para tres vistas: Tabla, Kanban (agrupado por cuadrante o por `Status`) y Calendario (anclado a una propiedad de tipo `Date`).

## 5. Alcance FUERA de este Bounded Context (exclusiones explícitas)

Los siguientes ámbitos **NO** pertenecen a este contexto y **NO** deben aparecer en el código, en los puertos ni en los endpoints generados:

- **[FUERA]** Autenticación, registro y gestión de sesiones de usuarios. Se asume que llega un `userId` ya validado.
- **[FUERA]** Autorización granular entre usuarios de un mismo Workspace (ACLs, roles). El usuario autenticado tiene acceso completo al Workspace.
- **[FUERA]** Notificaciones de cualquier tipo: no se envían correos, SMS, push ni notificaciones in-app. El sistema no expone endpoints `/notifications` ni dependencias hacia servicios de mensajería.
- **[FUERA]** Colaboración en tiempo real: no hay WebSockets, *presence*, cursores compartidos ni transformaciones operacionales.
- **[FUERA]** Facturación, planes de suscripción, cuotas y límites comerciales.
- **[FUERA]** Integraciones con calendarios externos (Google Calendar, Outlook, Apple Calendar, iCal).
- **[FUERA]** Analíticas, dashboards y *reporting* transversal entre Workspaces.
- **[FUERA]** Importación y exportación masiva desde/hacia otras herramientas de productividad.
- **[FUERA]** IA conversacional o asistentes dentro del producto (distinto de la IA que genera el código del laboratorio).

Cualquier requerimiento que caiga en estas categorías debe tratarse como *fuera de alcance* y rechazarse en la especificación, no implementarse con un *TODO*.

## 6. Supuestos

El sistema opera asumiendo las siguientes condiciones como ciertas. Si alguna se viola, el comportamiento queda indefinido:

- El usuario ya está autenticado cuando llega a este contexto; la identidad llega como `userId: string (uuid)` en los DTOs de entrada cuando se requiera.
- El `Workspace` y sus `Projects` ya existen, creados por otro Bounded Context que queda fuera del laboratorio.
- Todas las fechas se manejan internamente en **UTC**. La conversión a la zona horaria del usuario es responsabilidad de la capa de presentación, fuera de este contexto.

Para las restricciones técnicas del stack (lenguaje, runtime, base de datos, frameworks), ver `TECH_CONSTRAINTS.md §1`. Para las decisiones arquitectónicas derivadas de esas restricciones (como la estrategia de serialización de `PropertyValues`), ver `ARCHITECTURE.md §6`.

## 7. Glosario mínimo de términos de producto

Para el lenguaje ubicuo completo del dominio, consultar `DOMAIN.md §1` y `GLOSSARY.md`. A nivel de producto, basta con:

- **Workspace**: el espacio del usuario; contenedor raíz de todo lo demás.
- **Project**: contenedor de tareas dentro de un Workspace; una Task pertenece a exactamente uno.
- **Task**: la unidad de trabajo del sistema. Tiene urgencia, importancia, propiedades dinámicas y, posiblemente, subtareas.
- **Cuadrante (Quadrant)**: HACER / PLANIFICAR / DELEGAR / ELIMINAR, derivado siempre de `(urgency, importance)`.
- **Vista (View)**: proyección de solo lectura sobre un conjunto de Tasks (Tabla, Kanban, Calendario).

---

*Este archivo es parte del paquete de contexto del Bounded Context **Task Management**. Cualquier modificación requiere commit atómico separado con mensaje que comience por `docs(context):`.*
