import uuid
from typing import List, Optional, Dict, Any
from .project import Project
from .property import PropertySchema
from .exceptions import SchemaNotFoundError

class Workspace:
    """
    Aggregate Root Principal. Contiene la configuración y proyectos.
    """
    def __init__(self, name: str, workspace_id: Optional[str] = None, projects: Optional[List[Project]] = None):
        self.id = workspace_id or str(uuid.uuid4())
        self.name = name
        self.projects: List[Project] = projects if projects is not None else []
        self.property_schemas: Dict[str, PropertySchema] = {}
        
    def add_property_schema(self, schema: PropertySchema) -> None:
        """Registra un nuevo esquema de propiedad en el Workspace."""
        self.property_schemas[schema.name] = schema

    def set_task_property(self, project_id: str, task_id: str, property_name: str, value: Any) -> None:
        """
        Orquesta la actualización de propiedades garantizando INV-06.
        """
        if property_name not in self.property_schemas:
            raise SchemaNotFoundError(property_name)
            
        schema = self.property_schemas[property_name]
        schema.validate(value)
        
        project = self.get_project(project_id)
        task = project.get_task(task_id)
        
        if value is None:
            task.property_values.pop(property_name, None)
        else:
            task.property_values[property_name] = value
        
    def add_project(self, project: Project) -> None:
        self.projects.append(project)
        
    def get_project(self, project_id: str) -> Project:
        for p in self.projects:
            if p.id == project_id:
                return p
        raise ValueError("Project not found")
