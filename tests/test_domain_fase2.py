import pytest
from src.domain.task import Task
from src.domain.quadrant import Quadrant
from src.domain.project import Project
from src.domain.workspace import Workspace
from src.domain.property import PropertySchema, PropertyType
from src.domain.exceptions import HierarchyCycleError, MaxDepthExceededError, SchemaNotFoundError, InvalidPropertyValueError

def test_task_quadrant_derivation():
    """
    Verifica que la propiedad quadrant deriva el estado Eisenhower
    basándose en la urgencia y la importancia (INV-01, INV-02).
    """
    # HACER: urgencia=True, importancia=True
    t1 = Task(title="Fuego", urgency=True, importance=True)
    assert t1.quadrant == Quadrant.HACER

    # PLANIFICAR: urgencia=False, importancia=True
    t2 = Task(title="Estrategia", urgency=False, importance=True)
    assert t2.quadrant == Quadrant.PLANIFICAR

    # DELEGAR: urgencia=True, importancia=False
    t3 = Task(title="Interrupción", urgency=True, importance=False)
    assert t3.quadrant == Quadrant.DELEGAR

    # ELIMINAR: urgencia=False, importancia=False
    t4 = Task(title="Distracción", urgency=False, importance=False)
    assert t4.quadrant == Quadrant.ELIMINAR

def test_workspace_and_project_composition():
    """
    Verifica que el Workspace funciona como raíz de los proyectos
    y asegura que las Tareas guarden la coherencia del project_id (INV-05).
    """
    ws = Workspace(name="Mi Espacio")
    proj = Project(workspace_id=ws.id, name="Mi Proyecto")
    ws.add_project(proj)
    
    t = Task(title="Nueva Tarea")
    proj.add_task(t)
    
    assert len(ws.projects) == 1
    assert len(proj.tasks) == 1
    assert t.project_id == proj.id # INV-05 compliance

def test_hierarchy_happy_path_and_depth_limit():
    proj = Project(workspace_id="ws1", name="P1")
    t1 = Task(title="L1")
    t2 = Task(title="L2")
    t3 = Task(title="L3")
    t4 = Task(title="L4")
    
    for t in [t1, t2, t3, t4]:
        proj.add_task(t)

    # L1 (1) -> L2 (2) -> L3 (3). Esto debe funcionar.
    proj.attach_subtask(t1.id, t2.id)
    proj.attach_subtask(t2.id, t3.id)
    assert t2.parent_task_id == t1.id
    assert t3.parent_task_id == t2.id

    # Intentar L3 (3) -> L4 (4) debe fallar (INV-03)
    with pytest.raises(MaxDepthExceededError):
        proj.attach_subtask(t3.id, t4.id)

def test_hierarchy_cycle_prevention():
    proj = Project(workspace_id="ws1", name="P1")
    t1 = Task(title="L1")
    t2 = Task(title="L2")
    t3 = Task(title="L3")
    
    for t in [t1, t2, t3]:
        proj.add_task(t)

    proj.attach_subtask(t1.id, t2.id)
    proj.attach_subtask(t2.id, t3.id)

    # Intentar que T3 (hijo de T2, nieto de T1) sea padre de T1 (INV-04)
    with pytest.raises(HierarchyCycleError):
        proj.attach_subtask(t3.id, t1.id)
        
    # Intentar asignar una tarea como hija de sí misma
    with pytest.raises(HierarchyCycleError):
        proj.attach_subtask(t1.id, t1.id)

def test_recursive_subtree_validation():
    """
    Si movemos un subárbol completo, debe calcular correctamente que 
    el "paquete" completo no exceda la profundidad de 3.
    """
    proj = Project(workspace_id="ws1", name="P1")
    t_parent = Task(title="Padre Principal")
    t_child = Task(title="Hijo")
    t_grandchild = Task(title="Nieto")
    
    for t in [t_parent, t_child, t_grandchild]:
        proj.add_task(t)
        
    # Construimos el subárbol: t_child -> t_grandchild
    proj.attach_subtask(t_child.id, t_grandchild.id)
    
    # Intentar adjuntar un subárbol de 2 niveles a t_parent (1) es válido (1+2 = 3)
    proj.attach_subtask(t_parent.id, t_child.id)
    assert t_child.parent_task_id == t_parent.id
    
    # Pero si el t_parent ya estuviera en nivel 2, fallaría
    t_root = Task(title="Raíz")
    proj.add_task(t_root)
    with pytest.raises(MaxDepthExceededError):
        proj.attach_subtask(t_root.id, t_parent.id) # Raíz -> Padre Principal -> Hijo -> Nieto (4 niveles! Debe fallar al intentar)
    
    # Para probar eso correctamente, hagámoslo en otro orden:
    t_root2 = Task(title="Raíz 2")
    t_padre2 = Task(title="Padre 2")
    proj.add_task(t_root2)
    proj.add_task(t_padre2)
    proj.attach_subtask(t_root2.id, t_padre2.id) # Nivel 2
    
    # Ahora intentamos adjuntar el paquete t_child (que ya tiene a t_grandchild) a t_padre2
    # Nivel de t_padre2 = 2. Profundidad del subárbol de t_child = 2. Total = 4 (Excede 3).
    # Desvinculemos t_child primero para la prueba limpia
    t_child.parent_task_id = None
    
    with pytest.raises(MaxDepthExceededError):
        proj.attach_subtask(t_padre2.id, t_child.id)

def test_dynamic_properties_validation():
    """
    Verifica que la asignación de propiedades respete el esquema del Workspace (INV-06).
    """
    ws = Workspace(name="WS Custom Fields")
    proj = Project(workspace_id=ws.id, name="Proyecto Alpha")
    ws.add_project(proj)
    
    t1 = Task(title="Comprar leche")
    proj.add_task(t1)
    
    # Configurar esquemas
    status_schema = PropertySchema("Estado", PropertyType.STATUS, {"options": ["Backlog", "In Progress", "Done"]})
    tags_schema = PropertySchema("Etiquetas", PropertyType.MULTI_SELECT, {"options": ["Urgent", "Bug", "Feature"]})
    date_schema = PropertySchema("Fecha de entrega", PropertyType.DATE)
    
    ws.add_property_schema(status_schema)
    ws.add_property_schema(tags_schema)
    ws.add_property_schema(date_schema)

    # 1. Asignar propiedad válida (Status)
    ws.set_task_property(proj.id, t1.id, "Estado", "In Progress")
    assert t1.property_values["Estado"] == "In Progress"

    # 2. Intentar asignar un estado que no está en las opciones
    with pytest.raises(InvalidPropertyValueError):
        ws.set_task_property(proj.id, t1.id, "Estado", "Review")

    # 3. Asignar MultiSelect válido
    ws.set_task_property(proj.id, t1.id, "Etiquetas", ["Urgent", "Bug"])
    assert "Urgent" in t1.property_values["Etiquetas"]

    # 4. Intentar asignar MultiSelect inválido
    with pytest.raises(InvalidPropertyValueError):
        ws.set_task_property(proj.id, t1.id, "Etiquetas", ["Bug", "No Existe"])

    # 5. Intentar asignar Date inválido (no string)
    with pytest.raises(InvalidPropertyValueError):
        ws.set_task_property(proj.id, t1.id, "Fecha de entrega", 2026)

    # 6. Intentar asignar una propiedad a un esquema que no existe
    with pytest.raises(SchemaNotFoundError):
        ws.set_task_property(proj.id, t1.id, "Prioridad Fantasma", "Alta")
