import uuid
from enum import Enum
from dataclasses import dataclass, field

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

    def __post_init__(self):
        """Validates domain invariants upon creation."""
        if not self.title or not self.title.strip():
            raise InvalidTitleError()
