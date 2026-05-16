document.addEventListener('DOMContentLoaded', () => {
    // Referencias a elementos del DOM
    const titleInput = document.getElementById('new-task-title');
    const urgencyCheck = document.getElementById('check-urgency');
    const importanceCheck = document.getElementById('check-importance');
    const addBtn = document.getElementById('add-task-btn');
    
    // Elementos del Modal
    const modal = document.getElementById('task-modal');
    const closeBtn = document.querySelector('.close-btn');
    const editId = document.getElementById('edit-task-id');
    const editTitle = document.getElementById('edit-task-title');
    const editUrgency = document.getElementById('edit-urgency');
    const editImportance = document.getElementById('edit-importance');
    const saveTaskBtn = document.getElementById('save-task-btn');
    const deleteTaskBtn = document.getElementById('delete-task-btn');
    
    // Elementos de Subtareas
    const subtaskList = document.getElementById('subtask-list');
    const newSubtaskTitle = document.getElementById('new-subtask-title');
    const addSubtaskBtn = document.getElementById('add-subtask-btn');
    
    // Elementos de Esquemas (Custom Fields)
    const newSchemaName = document.getElementById('new-schema-name');
    const newSchemaType = document.getElementById('new-schema-type');
    const addSchemaBtn = document.getElementById('add-schema-btn');
    const dynamicPropertiesContainer = document.getElementById('dynamic-properties-container');
    
    // Elementos de Vistas
    const viewTabs = document.querySelectorAll('.tab-btn');
    const viewKanban = document.getElementById('view-kanban');
    const viewTable = document.getElementById('view-table');
    const tableHeadRow = document.getElementById('table-head-row');
    const tableBody = document.getElementById('table-body');
    
    let currentView = 'kanban';
    
    let currentBoardTasks = [];
    let currentSchemas = [];
    
    const lists = {
        'TODO': document.getElementById('list-TODO'),
        'DOING': document.getElementById('list-DOING'),
        'DONE': document.getElementById('list-DONE')
    };
    
    const counts = {
        'TODO': document.getElementById('count-TODO'),
        'DOING': document.getElementById('count-DOING'),
        'DONE': document.getElementById('count-DONE')
    };

    // Cerrar modal
    closeBtn.onclick = () => modal.style.display = "none";
    window.onclick = (e) => { if (e.target == modal) modal.style.display = "none"; }

    // Carga inicial del tablero
    fetchBoard();

    // Eventos
    addBtn.addEventListener('click', createTask);
    titleInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') createTask();
    });
    
    // Eventos de Vistas
    viewTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            const view = e.target.dataset.view;
            switchView(view);
        });
    });

    function switchView(view) {
        currentView = view;
        viewTabs.forEach(t => t.classList.remove('active'));
        document.querySelector(`.tab-btn[data-view="${view}"]`).classList.add('active');
        
        if (view === 'kanban') {
            viewKanban.style.display = 'grid';
            viewTable.style.display = 'none';
        } else {
            viewKanban.style.display = 'none';
            viewTable.style.display = 'block';
        }
        
        // Renderizar la vista activa
        if (currentView === 'kanban') {
            renderBoard(currentBoardTasks);
        } else {
            renderTable(currentBoardTasks, currentSchemas);
        }
    }

    // 1. OBTENER TABLERO (GET /api/board)
    async function fetchBoard() {
        try {
            const res = await fetch('/api/board');
            if (!res.ok) throw new Error('Error al cargar el tablero');
            const data = await res.json();
            currentBoardTasks = data.tasks || [];
            currentSchemas = data.schemas || [];
            
            if (currentView === 'kanban') {
                renderBoard(currentBoardTasks);
            } else {
                renderTable(currentBoardTasks, currentSchemas);
            }
        } catch (error) {
            showToast(error.message);
        }
    }

    // 2. CREAR TAREA (POST /api/tasks)
    async function createTask() {
        const title = titleInput.value.trim();
        const urgency = urgencyCheck.checked;
        const importance = importanceCheck.checked;
        
        if (!title) {
            showToast("El título de la tarea no puede estar vacío.");
            return;
        }

        try {
            const res = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, urgency, importance })
            });

            // Si falla, extraer el JSON de error del backend (Ej: Límite WIP, Título Inválido)
            if (!res.ok) {
                let errorData;
                try {
                    errorData = await res.json();
                } catch(e) {
                    throw new Error(`Error del servidor HTTP ${res.status}. Asegúrate de que el servidor esté corriendo con la última versión.`);
                }
                throw new Error(errorData.error || 'Error al crear la tarea');
            }

            titleInput.value = '';
            urgencyCheck.checked = false;
            importanceCheck.checked = false;
            fetchBoard(); // Recargar todo el tablero usando solo los datos del backend
        } catch (error) {
            showToast(error.message);
        }
    }

    // 3. MOVER TAREA (PATCH /api/tasks/<id>/move)
    window.moveTask = async function(taskId, targetState) {
        try {
            const res = await fetch(`/api/tasks/${taskId}/move`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_state: targetState })
            });

            // Manejo estricto de Errores de Negocio devueltos por el Dominio
            if (!res.ok) {
                let errorData;
                try {
                    errorData = await res.json();
                } catch(e) {
                    throw new Error(`Error del servidor HTTP ${res.status}. Asegúrate de que el servidor esté corriendo con la última versión.`);
                }
                throw new Error(errorData.error || 'Error al mover la tarea');
            }

            fetchBoard(); // Recargar el estado real desde la fuente de verdad (backend)
        } catch (error) {
            // Mostrar Toast con el error de negocio (Ej: Límite WIP excedido)
            showToast(error.message);
        }
    };

    // Lógica de Renderizado Reactiva (El estado real lo dicta la API)
    function renderBoard(tasks) {
        // Limpiar columnas
        Object.values(lists).forEach(list => list.innerHTML = '');
        
        // Reiniciar contadores
        const taskCounts = { 'TODO': 0, 'DOING': 0, 'DONE': 0 };

        // Dibujar tareas
        tasks.forEach(task => {
            const card = document.createElement('div');
            card.className = 'task-card';
            
            // Agregar evento para abrir el modal
            card.onclick = (e) => {
                if(e.target.tagName === 'BUTTON') return; // Ignorar clicks en los botones de "Mover"
                openModal(task);
            };

            // Construir botones según las transiciones válidas del Dominio
            let actionsHtml = '';
            if (task.state === 'TODO') {
                actionsHtml = `<button class="move-btn" onclick="moveTask('${task.id}', 'DOING')">Empezar</button>`;
            } else if (task.state === 'DOING') {
                actionsHtml = `<button class="move-btn" onclick="moveTask('${task.id}', 'DONE')">Completar</button>`;
            }

            // Construir etiqueta de Cuadrante si existe
            let quadrantHtml = '';
            if (task.quadrant) {
                const quadMap = {
                    "HACER": "quad-hacer",
                    "PLANIFICAR": "quad-planificar",
                    "DELEGAR": "quad-delegar",
                    "ELIMINAR": "quad-eliminar"
                };
                const iconMap = {
                    "HACER": "🔥",
                    "PLANIFICAR": "📅",
                    "DELEGAR": "👤",
                    "ELIMINAR": "🗑️"
                };
                quadrantHtml = `<div class="task-quadrant ${quadMap[task.quadrant]}">${iconMap[task.quadrant]} ${task.quadrant}</div>`;
            }

            card.innerHTML = `
                ${quadrantHtml}
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-actions">${actionsHtml}</div>
            `;
            
            lists[task.state].appendChild(card);
            taskCounts[task.state]++;
        });

        // Actualizar contadores
        Object.keys(counts).forEach(state => {
            counts[state].textContent = taskCounts[state];
        });
    }

    // Lógica de Renderizado de Tabla
    function renderTable(tasks, schemas) {
        // 1. Generar Encabezados
        tableHeadRow.innerHTML = `
            <th>Título</th>
            <th>Estado</th>
            <th>Cuadrante</th>
        `;
        
        schemas.forEach(schema => {
            const th = document.createElement('th');
            th.textContent = schema.name;
            tableHeadRow.appendChild(th);
        });

        // 2. Generar Filas
        tableBody.innerHTML = '';
        tasks.forEach(task => {
            const tr = document.createElement('tr');
            tr.onclick = () => openModal(task);
            
            // Cuadrante estático
            let quadrantHtml = '-';
            if (task.quadrant) {
                const quadMap = { "HACER": "quad-hacer", "PLANIFICAR": "quad-planificar", "DELEGAR": "quad-delegar", "ELIMINAR": "quad-eliminar" };
                const iconMap = { "HACER": "🔥", "PLANIFICAR": "📅", "DELEGAR": "👤", "ELIMINAR": "🗑️" };
                quadrantHtml = `<span class="table-quadrant ${quadMap[task.quadrant]}">${iconMap[task.quadrant]} ${task.quadrant}</span>`;
            }

            let html = `
                <td><strong>${escapeHtml(task.title)}</strong></td>
                <td><span class="count">${task.state}</span></td>
                <td>${quadrantHtml}</td>
            `;

            // Columnas Dinámicas
            const propValues = task.property_values || {};
            schemas.forEach(schema => {
                let val = propValues[schema.name];
                if (val === undefined || val === null) val = '-';
                else if (schema.type === 'BOOLEAN') val = val ? '✅' : '❌';
                
                html += `<td>${escapeHtml(val)}</td>`;
            });

            tr.innerHTML = html;
            tableBody.appendChild(tr);
        });
    }

    function openModal(task) {
        editId.value = task.id;
        editTitle.value = task.title;
        editUrgency.checked = task.urgency || false;
        editImportance.checked = task.importance || false;
        
        renderSubtasks(task.id);
        renderDynamicProperties(task);
        
        modal.style.display = "flex";
    }

    function renderSubtasks(parentId) {
        subtaskList.innerHTML = '';
        const subtasks = currentBoardTasks.filter(t => t.parent_task_id === parentId);
        
        if (subtasks.length === 0) {
            subtaskList.innerHTML = '<li style="color: var(--text-secondary); text-align: center;">No hay subtareas</li>';
            return;
        }

        subtasks.forEach(sub => {
            const li = document.createElement('li');
            li.innerHTML = `<span>${escapeHtml(sub.title)}</span> <span class="task-quadrant" style="font-size: 0.6rem; padding: 0.1rem 0.3rem;">${sub.state}</span>`;
            subtaskList.appendChild(li);
        });
    }

    function renderDynamicProperties(task) {
        dynamicPropertiesContainer.innerHTML = '';
        if (currentSchemas.length === 0) return;

        const propValues = task.property_values || {};

        currentSchemas.forEach(schema => {
            const div = document.createElement('div');
            div.className = 'prop-field';
            
            const label = document.createElement('label');
            label.textContent = schema.name;
            
            let input;
            if (schema.type === 'BOOLEAN') {
                input = document.createElement('input');
                input.type = 'checkbox';
                input.checked = propValues[schema.name] || false;
            } else if (schema.type === 'NUMBER') {
                input = document.createElement('input');
                input.type = 'number';
                input.step = 'any';
                input.value = propValues[schema.name] !== undefined ? propValues[schema.name] : '';
            } else if (schema.type === 'DATE') {
                input = document.createElement('input');
                input.type = 'date';
                input.value = propValues[schema.name] || '';
            } else {
                input = document.createElement('input');
                input.type = 'text';
                input.value = propValues[schema.name] || '';
            }
            
            input.id = `prop-${schema.name}`;
            input.dataset.type = schema.type;
            
            div.appendChild(label);
            div.appendChild(input);
            dynamicPropertiesContainer.appendChild(div);
        });
    }

    // 4. ACTUALIZAR TAREA (PUT /api/tasks/<id>)
    saveTaskBtn.onclick = async () => {
        const id = editId.value;
        const title = editTitle.value.trim();
        const urgency = editUrgency.checked;
        const importance = editImportance.checked;
        
        // Recolectar valores de propiedades dinámicas
        const property_values = {};
        currentSchemas.forEach(schema => {
            const input = document.getElementById(`prop-${schema.name}`);
            if (input) {
                let val;
                if (schema.type === 'BOOLEAN') val = input.checked;
                else if (schema.type === 'NUMBER') val = input.value !== '' ? Number(input.value) : null;
                else val = input.value !== '' ? input.value : null;
                
                // Enviar siempre, incluso null, para permitir vaciar campos
                property_values[schema.name] = val;
            }
        });

        if (!title) {
            showToast("El título no puede estar vacío.");
            return;
        }

        try {
            const res = await fetch(`/api/tasks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, urgency, importance, property_values })
            });

            if (!res.ok) {
                let errorData;
                try {
                    errorData = await res.json();
                } catch(e) {
                    throw new Error(`Error del servidor HTTP ${res.status}. Asegúrate de que el servidor esté corriendo con la última versión.`);
                }
                throw new Error(errorData.error || 'Error al actualizar');
            }

            modal.style.display = "none";
            fetchBoard();
        } catch (error) {
            showToast(error.message);
        }
    };

    // 5. ELIMINAR TAREA (DELETE /api/tasks/<id>)
    deleteTaskBtn.onclick = async () => {
        const id = editId.value;
        if(!confirm("¿Estás seguro de eliminar esta tarea? Se eliminarán también sus subtareas.")) return;

        try {
            const res = await fetch(`/api/tasks/${id}`, {
                method: 'DELETE'
            });

            if (!res.ok) {
                let errorData;
                try {
                    errorData = await res.json();
                } catch(e) {
                    throw new Error(`Error del servidor HTTP ${res.status}. Asegúrate de que el servidor esté corriendo con la última versión.`);
                }
                throw new Error(errorData.error || 'Error al eliminar');
            }

            modal.style.display = "none";
            fetchBoard();
        } catch (error) {
            showToast(error.message);
        }
    };

    // 6. CREAR SUBTAREA (POST /api/tasks/<id>/subtasks)
    addSubtaskBtn.onclick = async () => {
        const parentId = editId.value;
        const title = newSubtaskTitle.value.trim();

        if (!title) {
            showToast("El título de la subtarea no puede estar vacío.");
            return;
        }

        try {
            const res = await fetch(`/api/tasks/${parentId}/subtasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title })
            });

            if (!res.ok) {
                let errorData;
                try {
                    errorData = await res.json();
                } catch(e) {
                    throw new Error(`Error del servidor HTTP ${res.status}. Asegúrate de que el servidor fue reiniciado tras los últimos cambios.`);
                }
                throw new Error(errorData.error || 'Error al agregar subtarea');
            }

            newSubtaskTitle.value = '';
            
            // Recargar tablero sin cerrar el modal para que el usuario vea la nueva subtarea
            await fetchBoard();
            renderSubtasks(parentId);
            
        } catch (error) {
            showToast(error.message); // El backend devuelve "MaxDepthExceededError" aquí si se rompe la regla
        }
    };

    // 7. CREAR ESQUEMA (POST /api/schemas)
    addSchemaBtn.onclick = async () => {
        const name = newSchemaName.value.trim();
        const type = newSchemaType.value;

        if (!name) {
            showToast("El nombre de la propiedad no puede estar vacío.");
            return;
        }

        try {
            const res = await fetch(`/api/schemas`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, type })
            });

            if (!res.ok) {
                let errorData;
                try {
                    errorData = await res.json();
                } catch(e) {
                    throw new Error(`Error del servidor HTTP ${res.status}. Asegúrate de que el servidor fue reiniciado tras los últimos cambios.`);
                }
                throw new Error(errorData.error || 'Error al crear esquema');
            }

            newSchemaName.value = '';
            await fetchBoard();
            showToast("Propiedad creada correctamente", true); // Reusar showToast para éxito
            
        } catch (error) {
            showToast(error.message);
        }
    };

    // Funciones de Utilidad para UI
    function showToast(message, isSuccess = false) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = 'toast';
        if (isSuccess) {
            toast.style.backgroundColor = '#10b981'; // Verde éxito
        }
        
        toast.innerHTML = `
            <span>${escapeHtml(message)}</span>
            <span style="cursor:pointer; font-weight:bold;">&times;</span>
        `;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('fade-out');
            toast.addEventListener('animationend', () => toast.remove());
        }, 4000); // El toast dura 4 segundos
    }

    function escapeHtml(unsafe) {
        return (unsafe || '').toString()
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
});
