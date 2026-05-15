# ARCHITECTURE.md — Diseño de Software y Capas

El sistema debe implementarse siguiendo los principios de Clean Architecture y Arquitectura Hexagonal para garantizar la testabilidad y la independencia tecnológica.

## 1. Capas y Responsabilidades

### 1.1 Dominio (`src/domain/`)
- **Contenido:** Entidades (`Task`), Agregados (`Board`) e Invariantes (Límite WIP).
- **Regla:** Es la capa más interna. No puede importar nada de `application` o `infrastructure`.
- **Invariante Central:** El `Board` debe rechazar cualquier movimiento a `DOING` si ya existen 3 tareas en ese estado.

### 1.2 Aplicación (`src/application/`)
- **Contenido:** Casos de uso (ej. `CreateTask`, `MoveTask`, `GetBoard`).
- **Responsabilidad:** Orquestar la lógica llamando al dominio y utilizando los puertos de infraestructura.

### 1.3 Infraestructura (`src/infrastructure/`)
- **Entrada (Drivers):** Adaptador Flask que expone los endpoints HTTP.
- **Salida (Driven):** Adaptador de persistencia que escribe en el archivo JSON.

## 2. Puertos y Adaptadores (Inversión de Control)
- **Puerto de Persistencia:** Definir una interfaz/clase abstracta `RepositoryInterface` en la capa de aplicación.
- **Adaptador de Persistencia:** `JSONRepository` implementa la interfaz y maneja la lectura/escritura física en `database.json`.

## 3. Flujo de Control
1. El cliente (JS) envía una petición a Flask.
2. Flask invoca un Caso de Uso de la Capa de Aplicación.
3. El Caso de Uso recupera el Agregado (`Board`) del Repositorio.
4. El Caso de Uso ejecuta la operación en el Dominio.
5. Si la operación es válida, el Caso de Uso pide al Repositorio persistir los cambios.