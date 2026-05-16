import uuid
from typing import List, Optional
from .task import Task, TaskState
from .exceptions import (
    TaskNotFoundError, 
    InvalidStateTransitionError, 
    WipLimitExceededError,
    HierarchyCycleError,
    MaxDepthExceededError
)

WIP_LIMIT = 3

class Project:
    """
    Agregado que representa un Proyecto. Contiene y gestiona Tasks.
    Eventualmente absorberá la lógica del Board.
    """
    def __init__(self, workspace_id: str, name: str, project_id: Optional[str] = None, tasks: Optional[List[Task]] = None):
        self.id = project_id or str(uuid.uuid4())
        self.workspace_id = workspace_id
        self.name = name
        self.tasks: List[Task] = tasks if tasks is not None else []

    def add_task(self, task: Task) -> None:
        """Añade una tarea garantizando la coherencia del project_id (INV-05)"""
        task.project_id = self.id
        self.tasks.append(task)
        
    def get_task(self, task_id: str) -> Task:
        """Recupera una tarea por ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError()
        
    def move_task(self, task_id: str, target_state: TaskState) -> None:
        """
        Mueve una tarea aplicando las mismas reglas de flujo y WIP que el Board.
        (Preparando el terreno para reemplazar a Board).
        """
        task = self.get_task(task_id)

        # Enforce sequential state transition (TODO -> DOING -> DONE)
        is_valid_transition = False
        if task.state == TaskState.TODO and target_state == TaskState.DOING:
            is_valid_transition = True
        elif task.state == TaskState.DOING and target_state == TaskState.DONE:
            is_valid_transition = True

        if not is_valid_transition:
            raise InvalidStateTransitionError()

        # Enforce WIP Limit
        if target_state == TaskState.DOING:
            doing_count = sum(1 for t in self.tasks if t.state == TaskState.DOING)
            if doing_count >= WIP_LIMIT:
                raise WipLimitExceededError()

        task.state = target_state

    def _get_depth(self, task_id: str) -> int:
        """Calcula la profundidad de una tarea navegando hacia sus ancestros. Raíz = 1."""
        depth = 1
        curr = self.get_task(task_id)
        # Prevención de ciclos de código malicioso o estados inconsistentes al calcular
        visited = set([task_id])
        while curr.parent_task_id:
            if curr.parent_task_id in visited:
                raise HierarchyCycleError()
            visited.add(curr.parent_task_id)
            depth += 1
            curr = self.get_task(curr.parent_task_id)
        return depth

    def _get_max_subtree_depth(self, task_id: str) -> int:
        """Calcula la profundidad máxima del subárbol de una tarea (relativa a la propia tarea)."""
        children = [t for t in self.tasks if t.parent_task_id == task_id]
        if not children:
            return 1 # La tarea por sí sola tiene profundidad relativa de 1
        
        max_child_depth = 0
        for child in children:
            child_depth = self._get_max_subtree_depth(child.id)
            if child_depth > max_child_depth:
                max_child_depth = child_depth
        
        return 1 + max_child_depth

    def attach_subtask(self, parent_id: str, child_id: str) -> None:
        """
        Anida una tarea dentro de otra, garantizando que:
        1. Ambas tareas existen.
        2. No se formen ciclos (INV-04).
        3. No se exceda la profundidad de 3 (INV-03).
        """
        parent = self.get_task(parent_id)
        child = self.get_task(child_id)

        # 1. Chequeo directo para evitar que sea padre de sí misma
        if parent_id == child_id:
            raise HierarchyCycleError()

        # 2. Prevención de ciclos: El padre no puede ser descendiente del hijo
        # Navegamos desde el parent hacia arriba. Si encontramos al child_id, es un ciclo.
        curr = parent
        while curr.parent_task_id:
            if curr.parent_task_id == child_id:
                raise HierarchyCycleError()
            curr = self.get_task(curr.parent_task_id)
            
        # 3. Validación de profundidad (INV-03)
        # La nueva profundidad será: profundidad actual del padre + la profundidad del subárbol del hijo
        parent_absolute_depth = self._get_depth(parent_id)
        child_subtree_depth = self._get_max_subtree_depth(child_id)
        
        if parent_absolute_depth + child_subtree_depth > 3:
            raise MaxDepthExceededError()

        # 4. Aplicar el anidamiento
        child.parent_task_id = parent_id

    def update_task(self, task_id: str, title: str, urgency: bool, importance: bool) -> None:
        from .exceptions import InvalidTitleError
        if not title or not title.strip():
            raise InvalidTitleError()
            
        task = self.get_task(task_id)
        task.title = title
        task.urgency = urgency
        task.importance = importance

    def remove_task(self, task_id: str) -> None:
        """
        Elimina una tarea de la lista.
        Aplica Eliminación en Cascada (Cascade Delete) para subtareas.
        """
        task_to_remove = self.get_task(task_id)
        
        # Eliminar hijos en cascada
        children = [t for t in self.tasks if t.parent_task_id == task_id]
        for child in children:
            self.remove_task(child.id) # Recursivo
            
        self.tasks.remove(task_to_remove)
