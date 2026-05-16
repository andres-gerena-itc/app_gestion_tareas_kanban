from typing import Dict, Any, List
from src.domain.task import Task, TaskState
from src.domain.project import Project
from src.domain.workspace import Workspace
from src.domain.property import PropertySchema, PropertyType
from src.domain.views import KanbanView
from .repository import WorkspaceRepository

class CreateTaskUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    def execute(self, title: str, urgency: bool = False, importance: bool = False) -> Task:
        workspace = self.repo.get_workspace()
        
        if not workspace.projects:
            raise ValueError("No hay proyectos en el Workspace.")
        
        project = workspace.projects[0]
        task = Task(title=title, urgency=urgency, importance=importance)
        project.add_task(task)
        
        self.repo.save_workspace(workspace)
        return task

class MoveTaskUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    def execute(self, task_id: str, target_state: str) -> None:
        workspace = self.repo.get_workspace()
        
        if not workspace.projects:
            raise ValueError("No hay proyectos en el Workspace.")
            
        project = workspace.projects[0]
        
        try:
            state_enum = TaskState(target_state)
        except ValueError:
            raise ValueError(f"Estado '{target_state}' no es válido.")

        project.move_task(task_id, state_enum)
        self.repo.save_workspace(workspace)

class EditTaskUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    def execute(self, task_id: str, title: str, urgency: bool, importance: bool, property_values: Dict[str, Any] = None) -> None:
        workspace = self.repo.get_workspace()
        if not workspace.projects:
            raise ValueError("No hay proyectos en el Workspace.")
        project = workspace.projects[0]
        project.update_task(task_id, title, urgency, importance)
        
        if property_values is not None:
            for prop_name, prop_val in property_values.items():
                workspace.set_task_property(project.id, task_id, prop_name, prop_val)
                
        self.repo.save_workspace(workspace)

class DeleteTaskUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    def execute(self, task_id: str) -> None:
        workspace = self.repo.get_workspace()
        if not workspace.projects:
            raise ValueError("No hay proyectos en el Workspace.")
        project = workspace.projects[0]
        project.remove_task(task_id)
        self.repo.save_workspace(workspace)

class AddSubtaskUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    def execute(self, parent_id: str, title: str) -> Task:
        workspace = self.repo.get_workspace()
        if not workspace.projects:
            raise ValueError("No hay proyectos en el Workspace.")
        project = workspace.projects[0]
        
        # Crear la subtarea
        subtask = Task(title=title)
        project.add_task(subtask)
        
        # Anidar (Lanza HierarchyCycleError o MaxDepthExceededError si viola reglas)
        project.attach_subtask(parent_id, subtask.id)
        
        self.repo.save_workspace(workspace)
        return subtask

class AddSchemaUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    def execute(self, name: str, prop_type: str, required: bool = False, options: List[str] = None) -> None:
        workspace = self.repo.get_workspace()
        
        try:
            ptype = PropertyType(prop_type)
        except ValueError:
            raise ValueError(f"Tipo de propiedad '{prop_type}' no soportado.")
            
        config = {"required": required, "options": options or []}
        schema = PropertySchema(name=name, type=ptype, config=config)
        workspace.add_property_schema(schema)
        
        self.repo.save_workspace(workspace)

class GetKanbanViewUseCase:
    """
    Reemplaza a GetBoardUseCase. Retorna una Proyección (Vista) 
    sin acoplarse al agregado monolítico.
    """
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    def execute(self) -> Dict[str, Any]:
        workspace = self.repo.get_workspace()
        
        if not workspace.projects:
            return {"tasks": [], "schemas": []}
            
        return KanbanView.generate(workspace)
