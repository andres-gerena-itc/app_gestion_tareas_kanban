from enum import Enum

class Quadrant(Enum):
    """
    Representa los cuatro cuadrantes de la Matriz de Eisenhower.
    Es un valor derivado en tiempo real, nunca persistido.
    """
    HACER = "HACER"
    PLANIFICAR = "PLANIFICAR"
    DELEGAR = "DELEGAR"
    ELIMINAR = "ELIMINAR"
