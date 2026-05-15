# BITACORA.md — Registro de Decisiones y Validaciones

Este archivo documenta la evolución del proyecto generada con IA. Cada vez que se apruebe un código y se haga commit, se debe registrar aquí.

| Fecha | Paso | Descripción del Cambio | Archivos Modificados | Resultado / Pruebas | Hash del Commit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-05-15 | Inicial | Creación del paquete de contexto Markdown. | `context/*`, `specs/*`, `plan/*`, `prompts/*`| Aprobado | d00267e |
| 2026-05-15 | Paso 1 | Estructura inicial carpetas | | Aprobado | 6830b22 |
| 2026-05-15 | Paso 2 | Implementación del Dominio (Task, Board, Límite WIP). | `src/domain/exceptions.py`, `src/domain/task.py`, `src/domain/board.py` | Aprobado | `742d8bd` |
| 2026-05-15 | Paso 3 | Pruebas Unitarias del Dominio con pytest. | `tests/test_domain.py` | Aprobado (7/7 tests) | 3d77350 |
| 2026-05-15 | Paso 4 | Casos de Uso y Puerto del Repositorio (Inversión de Control). | `src/application/*` | Aprobado | bc013e1 |
| | | | | | |