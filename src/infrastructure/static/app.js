document.addEventListener('DOMContentLoaded', () => {
    // Referencias a elementos del DOM
    const titleInput = document.getElementById('new-task-title');
    const urgencyCheck = document.getElementById('check-urgency');
    const importanceCheck = document.getElementById('check-importance');
    const addBtn = document.getElementById('add-task-btn');
    
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

    // Carga inicial del tablero
    fetchBoard();

    // Eventos
    addBtn.addEventListener('click', createTask);
    titleInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') createTask();
    });

    // 1. OBTENER TABLERO (GET /api/board)
    async function fetchBoard() {
        try {
            const res = await fetch('/api/board');
            if (!res.ok) throw new Error('Error al cargar el tablero');
            const data = await res.json();
            renderBoard(data.tasks);
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
                const errorData = await res.json();
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
                const errorData = await res.json();
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

    // Funciones de Utilidad para UI
    function showToast(message) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `<span>⚠️ ${escapeHtml(message)}</span>`;
        
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
