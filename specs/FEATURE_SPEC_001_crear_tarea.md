# FEATURE_SPEC_001: Crear Tarea

## 1. Descripción
Define el proceso mediante el cual una nueva tarea (`Task`) es ingresada al sistema. Esta funcionalidad asegura que toda tarea inicie en el flujo correcto y con los datos mínimos obligatorios.

## 2. Precondiciones
- El sistema debe estar en ejecución.
- El repositorio de persistencia debe estar disponible.

## 3. Entradas
- `title` (string): El texto descriptivo de la tarea.

## 4. Reglas de Negocio
- **R1 - Título Obligatorio:** El `title` no puede ser nulo, vacío ni contener únicamente espacios en blanco.
- **R2 - Estado Inicial:** Toda nueva tarea debe ser instanciada estrictamente en el estado `TODO`.
- **R3 - Identidad:** A cada tarea se le debe asignar automáticamente un `id` único e irrepetible (UUID).

## 5. Flujo Principal (Camino Feliz)
1. El cliente solicita crear una tarea enviando un `title`.
2. El sistema valida que el `title` cumpla con R1.
3. El sistema genera una nueva entidad `Task` con un UUID generado y estado `TODO`.
4. El sistema agrega la tarea al `Board`.
5. El sistema guarda los cambios a través del Repositorio.
6. El sistema retorna la tarea creada (incluyendo su nuevo `id`).

## 6. Flujos Alternativos / Errores
- **E1 - Título Inválido:** Si el `title` incumple R1, el sistema debe rechazar la operación y lanzar un error `InvalidTitleError`. No se realiza ninguna persistencia.

## 7. Criterios de Aceptación (Para Pruebas Automatizadas)
- **AC-01.01:** Dado un título válido ("Comprar café"), cuando se solicita crear la tarea, entonces se retorna una tarea con ese título, un ID válido y el estado en `TODO`.
- **AC-01.02:** Dado un título vacío (""), cuando se solicita crear la tarea, entonces se lanza una excepción `InvalidTitleError` y el tablero no sufre modificaciones.