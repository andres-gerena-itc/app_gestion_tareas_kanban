import uuid
from typing import List, Optional
from .project import Project

class Workspace:
    """
    Aggregate Root Principal. Contiene la configuración y proyectos.
    """
    def __init__(self, name: str, workspace_id: Optional[str] = None, projects: Optional[List[Project]] = None):
        self.id = workspace_id or str(uuid.uuid4())
        self.name = name
        self.projects: List[Project] = projects if projects is not None else []
        self.property_schemas = {} # Espacio preparado para el Paso 12
        
    def add_project(self, project: Project) -> None:
        self.projects.append(project)
        
    def get_project(self, project_id: str) -> Project:
        for p in self.projects:
            if p.id == project_id:
                return p
        raise ValueError("Project not found")
