class DomainError(Exception):
    """Base class for all domain exceptions."""
    pass

class InvalidTitleError(DomainError):
    def __init__(self):
        super().__init__("El título de la tarea no puede estar vacío.")

class TaskNotFoundError(DomainError):
    def __init__(self):
        super().__init__("La tarea solicitada no existe en el tablero.")

class InvalidStateTransitionError(DomainError):
    def __init__(self):
        super().__init__("Transición de estado no permitida.")

class WipLimitExceededError(DomainError):
    def __init__(self):
        super().__init__("Límite WIP excedido. No se pueden tener más de 3 tareas en estado DOING.")
