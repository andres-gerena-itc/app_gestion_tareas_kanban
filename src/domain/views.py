from typing import Dict, Any, List
from .project import Project

class KanbanView:
    """
    Proyección (Vista) de lectura para un Proyecto.
    Transforma el estado actual del Proyecto en un formato Kanban clásico.
    Cumple con la arquitectura de CQRS/Proyecciones (INV-08).
    """
    @staticmethod
    def generate(workspace) -> Dict[str, Any]:
        if not workspace.projects:
            return {"tasks": [], "schemas": []}
        project = workspace.projects[0]
        tasks_data = [
            {
                "id": task.id,
                "title": task.title,
                "state": task.state.value,
                "quadrant": task.quadrant.value,
                "urgency": task.urgency,
                "importance": task.importance,
                "parent_task_id": task.parent_task_id,
                "property_values": task.property_values
            }
            for task in project.tasks
        ]
        
        schemas_data = [
            {
                "name": schema.name,
                "type": schema.type.value,
                "required": schema.config.get("required", False),
                "options": schema.config.get("options", [])
            }
            for schema in workspace.property_schemas.values()
        ]
        
        return {"tasks": tasks_data, "schemas": schemas_data}
