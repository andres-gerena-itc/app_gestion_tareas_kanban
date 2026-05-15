from abc import ABC, abstractmethod
from src.domain.board import Board

class BoardRepository(ABC):
    """
    Puerto de persistencia (interfaz) para el manejo de tableros.
    Permite a la capa de aplicación interactuar con el almacenamiento
    sin conocer detalles de infraestructura (ej. JSON, base de datos).
    """

    @abstractmethod
    def get_board(self) -> Board:
        """Recupera el tablero actual con todas sus tareas."""
        pass

    @abstractmethod
    def save_board(self, board: Board) -> None:
        """Persiste el estado actual del tablero y sus tareas."""
        pass
