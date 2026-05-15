from src.domain.task import Task, TaskState
from src.domain.board import Board
from src.application.repository import BoardRepository

class CreateTaskUseCase:
    """Orquesta la creación de una tarea y su adición al tablero."""
    
    def __init__(self, repository: BoardRepository):
        self.repository = repository

    def execute(self, title: str) -> Task:
        # 1. Recuperar el estado actual
        board = self.repository.get_board()
        
        # 2. Instanciar la entidad del dominio (aplica regla: Título Obligatorio y estado TODO)
        task = Task(title=title)
        
        # 3. Delegar lógica de negocio al agregado
        board.add_task(task)
        
        # 4. Persistir cambios
        self.repository.save_board(board)
        
        return task

class MoveTaskUseCase:
    """Orquesta el movimiento de una tarea en el tablero."""
    
    def __init__(self, repository: BoardRepository):
        self.repository = repository

    def execute(self, task_id: str, target_state: TaskState) -> None:
        # 1. Recuperar el estado actual
        board = self.repository.get_board()
        
        # 2. Delegar lógica de negocio (aplica reglas: Límite WIP y Transiciones válidas)
        board.move_task(task_id, target_state)
        
        # 3. Persistir cambios
        self.repository.save_board(board)

class GetBoardUseCase:
    """Obtiene el estado actual del tablero sin realizar alteraciones."""
    
    def __init__(self, repository: BoardRepository):
        self.repository = repository

    def execute(self) -> Board:
        # 1. Simplemente recupera y retorna la información
        return self.repository.get_board()
