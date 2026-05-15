import json
import os
from typing import Dict, Any

from src.application.repository import WorkspaceRepository
from src.domain.workspace import Workspace
from src.domain.project import Project
from src.domain.task import Task, TaskState
from src.domain.property import PropertySchema, PropertyType

class JSONWorkspaceRepository(WorkspaceRepository):
    def __init__(self, file_path: str = "data/database.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def _create_default_workspace(self) -> Workspace:
        ws = Workspace(name="Mi Espacio Personal")
        proj = Project(workspace_id=ws.id, name="Mi Primer Tablero")
        ws.add_project(proj)
        return ws

    def get_workspace(self) -> Workspace:
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            return self._create_default_workspace()

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Si el JSON es el formato antiguo (Board), retornamos uno nuevo para migrar
            if "projects" not in data:
                print("Base de datos en formato antiguo (Board). Se generará un nuevo Workspace.")
                return self._create_default_workspace()
                
            ws = Workspace(name=data["name"], workspace_id=data["id"])
            
            for schema_data in data.get("property_schemas", []):
                schema = PropertySchema(
                    name=schema_data["name"],
                    type=PropertyType(schema_data["type"]),
                    config=schema_data.get("config", {})
                )
                ws.add_property_schema(schema)
                
            for proj_data in data.get("projects", []):
                proj = Project(workspace_id=ws.id, name=proj_data["name"], project_id=proj_data["id"])
                
                for task_data in proj_data.get("tasks", []):
                    task = Task(
                        title=task_data["title"],
                        id=task_data["id"],
                        state=TaskState(task_data["state"]),
                        project_id=proj.id,
                        parent_task_id=task_data.get("parent_task_id"),
                        urgency=task_data.get("urgency", False),
                        importance=task_data.get("importance", False),
                        property_values=task_data.get("property_values", {})
                    )
                    proj.tasks.append(task)
                    
                ws.add_project(proj)
                
            return ws
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error reading JSON database, returning default. Error: {e}")
            return self._create_default_workspace()

    def save_workspace(self, workspace: Workspace) -> None:
        data = {
            "id": workspace.id,
            "name": workspace.name,
            "property_schemas": [
                {
                    "name": schema.name,
                    "type": schema.type.value,
                    "config": schema.config
                } for schema in workspace.property_schemas.values()
            ],
            "projects": [
                {
                    "id": proj.id,
                    "workspace_id": proj.workspace_id,
                    "name": proj.name,
                    "tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "state": task.state.value,
                            "project_id": task.project_id,
                            "parent_task_id": task.parent_task_id,
                            "urgency": task.urgency,
                            "importance": task.importance,
                            "property_values": task.property_values
                        } for task in proj.tasks
                    ]
                } for proj in workspace.projects
            ]
        }
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
