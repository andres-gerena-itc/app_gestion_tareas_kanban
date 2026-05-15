import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

from .exceptions import InvalidTitleError

class TaskState(Enum):
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"

@dataclass
class Task:
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: TaskState = field(default=TaskState.TODO)
    
    # === FASE 2: Expansión Multidimensional ===
    project_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    urgency: bool = False
    importance: bool = False

    def __post_init__(self):
        """Validates domain invariants upon creation."""
        if not self.title or not self.title.strip():
            raise InvalidTitleError()
            
    @property
    def quadrant(self):
        """
        Deriva el Cuadrante de Eisenhower en tiempo real (INV-01, INV-02).
        Lógica limpia y centralizada.
        """
        from .quadrant import Quadrant
        
        if self.urgency and self.importance:
            return Quadrant.HACER
        elif not self.urgency and self.importance:
            return Quadrant.PLANIFICAR
        elif self.urgency and not self.importance:
            return Quadrant.DELEGAR
        else:
            return Quadrant.ELIMINAR
