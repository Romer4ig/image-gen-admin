/**
 * Инициализация страницы коллекций
 */
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initTooltips();
    initPromptEditor();
    initCollectionTable();
    initTasksFilter();
    initBulkGeneration();
    
    // Обновление счетчика задач
    updatePendingTasksCount();
    setInterval(updatePendingTasksCount, 10000);
});

/**
 * Инициализация всплывающих подсказок
 */
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Инициализация редактора промптов с автосохранением
 */
function initPromptEditor() {
    document.querySelectorAll('.prompt-text').forEach(textarea => {
        // Сохраняем исходное значение при клике для сравнения
        textarea.addEventListener('focus', function() {
            this.dataset.currentValue = this.value;
        });
        
        // При потере фокуса проверяем, изменился ли текст
        textarea.addEventListener('blur', function() {
            const collectionId = this.closest('.prompt-editor').dataset.collectionId;
            const currentValue = this.value;
            
            // Проверяем, изменилось ли значение
            if (currentValue !== this.dataset.currentValue) {
                savePrompt(collectionId, currentValue, textarea);
            }
        });
        
        // Обрабатываем нажатие Ctrl+Enter для быстрого сохранения
        textarea.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                const collectionId = this.closest('.prompt-editor').dataset.collectionId;
                const currentValue = this.value;
                savePrompt(collectionId, currentValue, textarea);
            }
        });
    });
}

/**
 * Сохранение промпта через AJAX
 */
function savePrompt(collectionId, promptText, textarea) {
    // Показываем индикатор сохранения через border
    textarea.classList.add('saving-prompt');
    
    // Отправляем AJAX запрос на сохранение
    fetch('/collections/update_prompt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            collection_id: collectionId,
            prompt: promptText
        })
    })
    .then(response => response.json())
    .then(data => {
        // Убираем класс сохранения
        textarea.classList.remove('saving-prompt');
        
        if (data.success) {
            // Обновляем оригинальное значение
            textarea.dataset.originalValue = promptText;
            textarea.dataset.currentValue = promptText;
            
            // Показываем успешное сохранение через border
            textarea.classList.add('saved-prompt');
            
            // Убираем индикатор через 2 секунды
            setTimeout(() => {
                textarea.classList.remove('saved-prompt');
            }, 2000);
        } else {
            // Показываем ошибку через border
            textarea.classList.add('error-prompt');
            
            // Убираем индикатор через 2 секунды
            setTimeout(() => {
                textarea.classList.remove('error-prompt');
            }, 2000);
            
            console.error('Ошибка сохранения:', data.error || 'не удалось сохранить');
        }
    })
    .catch(error => {
        // Убираем класс сохранения
        textarea.classList.remove('saving-prompt');
        
        // Показываем ошибку через border
        textarea.classList.add('error-prompt');
        
        // Убираем индикатор через 2 секунды
        setTimeout(() => {
            textarea.classList.remove('error-prompt');
        }, 2000);
        
        console.error('Ошибка соединения:', error);
    });
}

/**
 * Получение CSRF токена из куки
 */
function getCsrfToken() {
    const name = 'csrf_token=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    
    for(let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    return '';
}

/**
 * Инициализация таблицы коллекций
 */
function initCollectionTable() {
    // Анимация при удалении коллекции
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('delete-collection')) {
            e.preventDefault();
            
            if (confirm('Вы уверены, что хотите удалить эту коллекцию?')) {
                const deleteForm = document.querySelector(`#delete-form-${e.target.dataset.id}`);
                const tableRow = e.target.closest('tr');
                
                tableRow.classList.add('fade-out');
                
                setTimeout(() => {
                    deleteForm.submit();
                }, 500);
            }
        }
    });
    
    // Подсветка строк при наведении
    document.querySelectorAll('#collectionsTable tbody tr').forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.classList.add('table-active');
        });
        row.addEventListener('mouseleave', function() {
            this.classList.remove('table-active');
        });
    });
}

/**
 * Обновление счетчика ожидающих задач
 */
function updatePendingTasksCount() {
    fetch('/tasks/pending-tasks-count')
        .then(response => response.json())
        .then(data => {
            const countElement = document.getElementById('pendingTasksCount');
            if (countElement) {
                if (data.count > 0) {
                    countElement.textContent = data.count;
                    countElement.style.display = 'inline-block';
                } else {
                    countElement.style.display = 'none';
                }
            }
        })
        .catch(error => console.error('Error updating pending tasks count:', error));
}

/**
 * Инициализация фильтров на странице задач
 */
function initTasksFilter() {
    // Обработчик изменения статуса для фильтрации
    const statusFilter = document.getElementById('statusFilter');
    const collectionFilter = document.getElementById('collectionFilter');
    const projectFilter = document.getElementById('projectFilter');
    
    // Проверяем наличие элементов фильтра (они есть только на странице задач)
    if (!statusFilter || !collectionFilter || !projectFilter) {
        return;
    }
    
    // Функция для применения фильтров и перенаправления
    function applyFilters() {
        const statusValue = statusFilter.value;
        const collectionValue = collectionFilter.value;
        const projectValue = projectFilter.value;
        
        let url = '/tasks/?';
        const params = [];
        
        if (statusValue) {
            params.push(`status=${statusValue}`);
        }
        
        if (collectionValue) {
            params.push(`collection_id=${collectionValue}`);
        }
        
        if (projectValue) {
            params.push(`project_id=${projectValue}`);
        }
        
        window.location.href = url + params.join('&');
    }
    
    // Устанавливаем обработчики
    statusFilter.addEventListener('change', applyFilters);
    collectionFilter.addEventListener('change', applyFilters);
    projectFilter.addEventListener('change', applyFilters);
}

/**
 * Инициализация функциональности массовой генерации
 */
function initBulkGeneration() {
    const selectAllCheckbox = document.getElementById('selectAllCollections');
    const collectionCheckboxes = document.querySelectorAll('.collection-checkbox');
    const bulkGenerateBtn = document.getElementById('bulkGenerateBtn');
    const bulkProjectSelect = document.getElementById('bulkProjectSelect');
    const bulkForm = document.getElementById('bulkGenerateForm');
    
    if (!selectAllCheckbox || !bulkGenerateBtn || !bulkForm) {
        return; // Не на странице коллекций
    }
    
    // Обработчик для выбора всех коллекций
    selectAllCheckbox.addEventListener('change', function() {
        const isChecked = this.checked;
        
        collectionCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
        
       
    });
    
    
}

/**
 * Показать всплывающее уведомление
 * @param {string} message - текст уведомления
 * @param {string} type - тип уведомления (success, danger, warning, info)
 */
function showToast(message, type = 'info') {
    // Создаем контейнер для тостов, если его нет
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    // Создаем элемент toast
    const toastId = 'toast-' + Date.now();
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.id = toastId;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');

    // Создаем содержимое toast
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    // Добавляем toast в контейнер
    toastContainer.appendChild(toastEl);

    // Инициализируем и показываем toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 3000
    });
    toast.show();

    // Удаляем toast после скрытия
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}
function syncSettings() {
    const btn = document.querySelector('.sync-btn');
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div> Синхронизация...';

    fetch('/settings/sync-settings', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Настройки успешно синхронизированы!');
            location.reload();
        } else {
            alert('Ошибка синхронизации: ' + data.error);
        }
    })
    .catch(error => {
        alert('Ошибка сети: ' + error);
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-arrow-repeat"></i> Синхронизировать';
    });
}
