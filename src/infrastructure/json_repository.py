import json
import os
from typing import Dict, Any, List

from src.application.repository import BoardRepository
from src.domain.board import Board
from src.domain.task import Task, TaskState

class JSONBoardRepository(BoardRepository):
    """
    Implementación en infraestructura del puerto BoardRepository usando un archivo JSON local.
    """
    def __init__(self, file_path: str = "data/database.json"):
        self.file_path = file_path

    def get_board(self) -> Board:
        """
        Lee el archivo JSON, mapea los diccionarios a objetos de dominio puros y 
        retorna la entidad Aggregate `Board`. Retorna un tablero vacío si no hay archivo.
        """
        if not os.path.exists(self.file_path):
            return Board()
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            # Si el archivo está vacío o corrupto, retornamos un tablero nuevo
            return Board()
        
        # Mapeo de Infraestructura (JSON/Dict) a Dominio
        tasks: List[Task] = []
        for task_dict in data.get("tasks", []):
            task = Task(
                id=task_dict["id"],
                title=task_dict["title"],
                state=TaskState(task_dict["state"])
            )
            tasks.append(task)
            
        return Board(tasks=tasks)

    def save_board(self, board: Board) -> None:
        """
        Mapea el Aggregate `Board` a una estructura de diccionario nativa y 
        lo persiste en el archivo JSON.
        """
        # Mapeo de Dominio a Infraestructura (Dict/JSON)
        tasks_list = []
        for task in board.tasks:
            tasks_list.append({
                "id": task.id,
                "title": task.title,
                "state": task.state.value
            })
            
        data = {
            "tasks": tasks_list
        }
        
        # Asegurar que el directorio de destino exista
        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
        
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
