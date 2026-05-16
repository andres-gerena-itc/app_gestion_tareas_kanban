import sys
import os

# Añadir el directorio raíz del proyecto al sys.path para permitir ejecución directa
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask, request, jsonify, send_from_directory
from src.domain.task import TaskState
from src.domain.exceptions import DomainError
from src.application.use_cases import CreateTaskUseCase, MoveTaskUseCase, GetKanbanViewUseCase, EditTaskUseCase, DeleteTaskUseCase, AddSubtaskUseCase, AddSchemaUseCase
from src.infrastructure.json_repository import JSONWorkspaceRepository

# Añadimos parámetros para servir archivos estáticos desde el directorio 'static'
app = Flask(__name__, static_folder='static', static_url_path='')

# ==========================================
# Configuración de Inyección de Dependencias
# ==========================================
repository = JSONWorkspaceRepository(file_path="data/database.json")
create_task_uc = CreateTaskUseCase(repository)
move_task_uc = MoveTaskUseCase(repository)
get_kanban_view_uc = GetKanbanViewUseCase(repository)
edit_task_uc = EditTaskUseCase(repository)
delete_task_uc = DeleteTaskUseCase(repository)
add_subtask_uc = AddSubtaskUseCase(repository)
add_schema_uc = AddSchemaUseCase(repository)

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
    return jsonify(get_kanban_view_uc.execute()), 200

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Crea una nueva tarea."""
    data = request.get_json() or {}
    title = data.get('title')
    urgency = data.get('urgency', False)
    importance = data.get('importance', False)
    
    # La validación de negocio ocurre en el dominio a través del caso de uso.
    # Flask solo actúa como traductor de HTTP a Objetos/Llamadas de Aplicación.
    task = create_task_uc.execute(title, urgency, importance)
    
    return jsonify({
        "id": task.id,
        "title": task.title,
        "state": task.state.value,
        "quadrant": task.quadrant.value
    }), 201

@app.route('/api/tasks/<task_id>/move', methods=['PATCH'])
def move_task(task_id):
    """Mueve una tarea a un nuevo estado."""
    data = request.get_json() or {}
    target_state_str = data.get('target_state', '')
    
    # Transforma la excepción si se da el caso
    try:
        move_task_uc.execute(task_id, target_state_str) # El use case ya espera el string y lo valida
    except Exception as e:
        raise
        
    return jsonify({"message": "Tarea movida exitosamente"}), 200

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Actualiza los datos básicos de una tarea."""
    data = request.get_json() or {}
    title = data.get('title')
    urgency = data.get('urgency', False)
    importance = data.get('importance', False)
    property_values = data.get('property_values', {})
    
    edit_task_uc.execute(task_id, title, urgency, importance, property_values)
    return jsonify({"message": "Tarea actualizada exitosamente"}), 200

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Elimina una tarea y sus descendientes."""
    delete_task_uc.execute(task_id)
    return jsonify({"message": "Tarea eliminada exitosamente"}), 200

@app.route('/api/tasks/<task_id>/subtasks', methods=['POST'])
def add_subtask(task_id):
    """Crea y anida una subtarea bajo una tarea existente."""
    data = request.get_json() or {}
    title = data.get('title')
    
    subtask = add_subtask_uc.execute(task_id, title)
    return jsonify({
        "id": subtask.id,
        "title": subtask.title,
        "state": subtask.state.value,
        "parent_task_id": subtask.parent_task_id
    }), 201

@app.route('/api/schemas', methods=['POST'])
def add_schema():
    """Crea un nuevo esquema de propiedad para el Workspace."""
    data = request.get_json() or {}
    name = data.get('name')
    prop_type = data.get('type')
    required = data.get('required', False)
    
    add_schema_uc.execute(name, prop_type, required)
    return jsonify({"message": "Esquema creado exitosamente"}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
