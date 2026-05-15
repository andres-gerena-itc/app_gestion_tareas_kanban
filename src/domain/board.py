from typing import List, Optional
from .task import Task, TaskState
from .exceptions import (
    TaskNotFoundError,
    InvalidStateTransitionError,
    WipLimitExceededError
)

WIP_LIMIT = 3

class Board:
    """
    @deprecated: Este agregado monolítico será descontinuado y absorbido
    por la lógica de vistas (Views) a partir del Project en los Pasos 13 y 14.
    Se mantiene temporalmente para retrocompatibilidad con el frontend.
    """
    def __init__(self, tasks: Optional[List[Task]] = None):
        self.tasks: List[Task] = tasks if tasks is not None else []

    def add_task(self, task: Task) -> None:
        """Adds a new task to the board."""
        self.tasks.append(task)

    def get_task(self, task_id: str) -> Task:
        """Retrieves a task by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError()

    def move_task(self, task_id: str, target_state: TaskState) -> None:
        """
        Moves a task to a target state, enforcing sequential flow and the WIP limit.
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
