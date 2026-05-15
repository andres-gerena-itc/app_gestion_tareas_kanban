from flask import Flask, request, jsonify

# Dominio
from src.domain.task import TaskState
from src.domain.exceptions import DomainError

# Aplicación (Casos de Uso)
from src.application.use_cases import CreateTaskUseCase, MoveTaskUseCase, GetBoardUseCase

# Infraestructura (Adaptador)
from src.infrastructure.json_repository import JSONBoardRepository

# Añadimos parámetros para servir archivos estáticos desde el directorio 'static'
app = Flask(__name__, static_folder='static', static_url_path='')

# ==========================================
# Configuración de Inyección de Dependencias
# ==========================================
repository = JSONBoardRepository()
create_task_uc = CreateTaskUseCase(repository)
move_task_uc = MoveTaskUseCase(repository)
get_board_uc = GetBoardUseCase(repository)

# ==========================================
# Manejo de Errores de Dominio
# ==========================================
@app.errorhandler(DomainError)
def handle_domain_error(error):
    """
    Captura excepciones lanzadas por el dominio (InvalidTitleError, WipLimitExceededError,
    InvalidStateTransitionError, TaskNotFoundError) y las convierte en una respuesta HTTP 400.
    """
    return jsonify({"error": str(error)}), 400

# ==========================================
# Endpoints HTTP
# ==========================================

@app.route('/')
def serve_index():
    """Sirve el frontend Vanilla JS."""
    return app.send_static_file('index.html')

@app.route('/api/board', methods=['GET'])
def get_board():
    """Retorna el estado actual del tablero y sus tareas."""
    board = get_board_uc.execute()
    tasks_data = [
        {
            "id": task.id,
            "title": task.title,
            "state": task.state.value
        }
        for task in board.tasks
    ]
    return jsonify({"tasks": tasks_data}), 200

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Crea una nueva tarea."""
    data = request.get_json() or {}
    title = data.get('title')
    
    # La validación de negocio ocurre en el dominio a través del caso de uso.
    # Flask solo actúa como traductor de HTTP a Objetos/Llamadas de Aplicación.
    task = create_task_uc.execute(title)
    
    return jsonify({
        "id": task.id,
        "title": task.title,
        "state": task.state.value
    }), 201

@app.route('/api/tasks/<task_id>/move', methods=['PATCH'])
def move_task(task_id):
    """Mueve una tarea a un nuevo estado."""
    data = request.get_json() or {}
    target_state_str = data.get('target_state', '')
    
    try:
        # Transformar string de request a Enum de Dominio
        target_state = TaskState(target_state_str)
    except ValueError:
        return jsonify({"error": f"Estado '{target_state_str}' no es válido."}), 400
        
    # Las reglas de negocio (Límite WIP, transiciones) se ejecutan en el dominio.
    move_task_uc.execute(task_id, target_state)
    
    return jsonify({"message": "Tarea movida exitosamente"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
