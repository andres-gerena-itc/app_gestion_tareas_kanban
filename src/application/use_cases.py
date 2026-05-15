from typing import Dict, Any, List
from src.domain.task import Task, TaskState
from src.domain.project import Project
from src.domain.workspace import Workspace
from src.domain.views import KanbanView
from .repository import WorkspaceRepository

class CreateTaskUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    def execute(self, title: str) -> Task:
        workspace = self.repo.get_workspace()
        
        if not workspace.projects:
            raise ValueError("No hay proyectos en el Workspace.")
        
        project = workspace.projects[0]
        task = Task(title=title)
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
            return {"TODO": [], "DOING": [], "DONE": []}
            
        project = workspace.projects[0]
        return KanbanView.generate(project)
