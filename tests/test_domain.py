import pytest
from src.domain.task import Task, TaskState
from src.domain.board import Board
from src.domain.exceptions import (
    InvalidTitleError,
    TaskNotFoundError,
    InvalidStateTransitionError,
    WipLimitExceededError
)

# ==========================================
# FEATURE_SPEC_001: Crear Tarea
# ==========================================

def test_ac_01_01_create_task_with_valid_title():
    """
    AC-01.01: Dado un título válido ("Comprar café"), cuando se solicita crear la tarea, 
    entonces se retorna una tarea con ese título, un ID válido y el estado en TODO.
    """
    title = "Comprar café"
    task = Task(title=title)
    
    assert task.title == title
    assert task.id is not None
    assert isinstance(task.id, str)
    assert task.state == TaskState.TODO

def test_ac_01_02_create_task_with_empty_title_raises_error():
    """
    AC-01.02: Dado un título vacío (""), cuando se solicita crear la tarea, 
    entonces se lanza una excepción InvalidTitleError.
    """
    with pytest.raises(InvalidTitleError):
        Task(title="")
        
    with pytest.raises(InvalidTitleError):
        Task(title="   ")


# ==========================================
# FEATURE_SPEC_002: Mover Tarea (Flujo y Límite WIP)
# ==========================================

def test_ac_02_01_move_task_from_todo_to_doing():
    """
    AC-02.01: Dada una tarea en TODO y 0 tareas en DOING, 
    cuando se mueve la tarea a DOING, entonces su estado se actualiza exitosamente.
    """
    board = Board()
    task = Task(title="Tarea de prueba")
    board.add_task(task)
    
    board.move_task(task.id, TaskState.DOING)
    
    assert task.state == TaskState.DOING

def test_ac_02_02_move_task_from_doing_to_done():
    """
    AC-02.02: Dada una tarea en DOING, cuando se mueve a DONE, 
    entonces su estado se actualiza exitosamente.
    """
    board = Board()
    task = Task(title="Tarea de prueba")
    task.state = TaskState.DOING # Setup inicial
    board.add_task(task)
    
    board.move_task(task.id, TaskState.DONE)
    
    assert task.state == TaskState.DONE

def test_ac_02_03_wip_limit_exceeded_raises_error():
    """
    AC-02.03: Dada una tarea en TODO y 3 tareas ya existentes en DOING, 
    cuando se intenta mover la tarea a DOING, entonces se lanza WipLimitExceededError 
    y la tarea original permanece en TODO.
    """
    board = Board()
    
    # Agregar 3 tareas y moverlas a DOING
    for i in range(3):
        t = Task(title=f"Tarea en progreso {i}")
        board.add_task(t)
        board.move_task(t.id, TaskState.DOING)
        
    # Crear una nueva tarea en TODO
    new_task = Task(title="Nueva tarea")
    board.add_task(new_task)
    
    # Intentar moverla a DOING
    with pytest.raises(WipLimitExceededError):
        board.move_task(new_task.id, TaskState.DOING)
        
    # El estado original no debió cambiar
    assert new_task.state == TaskState.TODO

def test_ac_02_04_invalid_state_transition_raises_error():
    """
    AC-02.04: Dada una tarea en TODO, cuando se intenta mover directamente a DONE, 
    entonces se lanza InvalidStateTransitionError.
    """
    board = Board()
    task = Task(title="Tarea de prueba")
    board.add_task(task)
    
    with pytest.raises(InvalidStateTransitionError):
        board.move_task(task.id, TaskState.DONE)
        
    # El estado original no debió cambiar
    assert task.state == TaskState.TODO

# ==========================================
# Pruebas adicionales de robustness
# ==========================================

def test_move_nonexistent_task_raises_error():
    """Prueba que intentar mover una tarea que no está en el tablero lanza TaskNotFoundError."""
    board = Board()
    with pytest.raises(TaskNotFoundError):
        board.move_task("id-falso", TaskState.DOING)
