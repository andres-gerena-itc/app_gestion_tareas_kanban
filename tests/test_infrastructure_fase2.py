import os
import json
import pytest
from src.infrastructure.json_repository import JSONWorkspaceRepository
from src.domain.workspace import Workspace
from src.domain.project import Project
from src.domain.task import Task
from src.domain.property import PropertySchema, PropertyType

def test_json_workspace_repository_mapping(tmp_path):
    """
    Verifica que el repositorio mapea correctamente Workspace, Project, Task 
    y PropertySchemas hacia y desde JSON.
    """
    file_path = tmp_path / "test_db.json"
    repo = JSONWorkspaceRepository(file_path=str(file_path))
    
    # Crear la estructura de dominio
    ws = Workspace(name="Test WS")
    
    schema = PropertySchema("Prioridad", PropertyType.SELECT, {"options": ["Alta", "Baja"]})
    ws.add_property_schema(schema)
    
    proj = Project(workspace_id=ws.id, name="Test Project")
    ws.add_project(proj)
    
    t = Task(title="Test Task")
    t.property_values["Prioridad"] = "Alta"
    proj.add_task(t)
    
    # Guardar
    repo.save_workspace(ws)
    
    # Asegurar que el archivo se creó
    assert os.path.exists(file_path)
    
    # Leer en un nuevo repo
    new_repo = JSONWorkspaceRepository(file_path=str(file_path))
    loaded_ws = new_repo.get_workspace()
    
    assert loaded_ws.id == ws.id
    assert loaded_ws.name == "Test WS"
    assert "Prioridad" in loaded_ws.property_schemas
    
    loaded_proj = loaded_ws.projects[0]
    assert loaded_proj.id == proj.id
    assert loaded_proj.name == "Test Project"
    
    loaded_task = loaded_proj.tasks[0]
    assert loaded_task.id == t.id
    assert loaded_task.title == "Test Task"
    assert loaded_task.property_values["Prioridad"] == "Alta"
