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

class HierarchyCycleError(DomainError):
    def __init__(self):
        super().__init__("Ciclo de jerarquía detectado. Una tarea no puede ser hija de sí misma ni de sus propios descendientes.")

class MaxDepthExceededError(DomainError):
    def __init__(self):
        super().__init__("Profundidad máxima excedida. El árbol de tareas no puede superar los 3 niveles.")

class SchemaNotFoundError(DomainError):
    def __init__(self, property_name: str):
        super().__init__(f"No existe un esquema de propiedad llamado '{property_name}' en el Workspace.")

class InvalidPropertyValueError(DomainError):
    def __init__(self, message: str):
        super().__init__(message)
