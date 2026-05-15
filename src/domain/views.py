from typing import Dict, Any, List
from .project import Project

class KanbanView:
    """
    Proyección (Vista) de lectura para un Proyecto.
    Transforma el estado actual del Proyecto en un formato Kanban clásico.
    Cumple con la arquitectura de CQRS/Proyecciones (INV-08).
    """
    @staticmethod
    def generate(project: Project) -> Dict[str, Any]:
        tasks_data = [
            {
                "id": task.id,
                "title": task.title,
                "state": task.state.value
            }
            for task in project.tasks
        ]
        return {"tasks": tasks_data}
