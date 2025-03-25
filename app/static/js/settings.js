// Функция для обновления списков параметров Stable Diffusion
function updateSDParameters() {
    const apiUrlInput = document.getElementById('api_url');
    const samplerSelect = document.getElementById('default_sampler_name');
    const schedulerSelect = document.getElementById('default_scheduler');
    const sdModelSelect = document.getElementById('default_sd_model');
    
    // Получаем значение API URL
    const apiUrl = apiUrlInput.value.trim();
    
    if (!apiUrl) {
        return; // Пустой URL - просто выходим
    }
    
    // Сохраним текущие выбранные значения
    const currentSampler = samplerSelect.value;
    const currentScheduler = schedulerSelect.value;
    const currentSdModel = sdModelSelect.value;
    
    // Функция для обновления списка с сохранением выбранного значения
    function updateSelect(select, data, valueProp = 'name', titleProp = null) {
        const currentValue = select.value;
        
        // Сохраняем первую опцию (если это "Использовать текущую модель")
        let firstOption = null;
        if (select.options.length > 0 && !select.options[0].value) {
            firstOption = select.options[0].cloneNode(true);
        }
        
        // Очищаем текущие опции
        select.innerHTML = '';
        
        // Восстанавливаем первую опцию, если она была
        if (firstOption) {
            select.appendChild(firstOption);
        }
        
        // Добавляем новые опции
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item[titleProp || valueProp];
            option.textContent = item[titleProp || valueProp];
            
            // Если это было выбрано ранее, отмечаем как selected
            if (item[titleProp || valueProp] === currentValue) {
                option.selected = true;
            }
            
            select.appendChild(option);
        });
    }
    
    // Обновляем список семплеров
    fetch('/settings/api/samplers')
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка получения списка семплеров');
            }
            return response.json();
        })
        .then(data => {
            if (Array.isArray(data)) {
                updateSelect(samplerSelect, data);
                
                // Выбираем сохраненное значение, если оно существует в новом списке
                if (currentSampler) {
                    const exists = Array.from(samplerSelect.options).some(
                        option => option.value === currentSampler
                    );
                    
                    if (exists) {
                        samplerSelect.value = currentSampler;
                    }
                }
            }
        })
        .catch(error => {
            console.error('Ошибка при загрузке семплеров:', error);
        });
    
    // Обновляем список планировщиков
    fetch('/settings/api/schedulers')
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка получения списка планировщиков');
            }
            return response.json();
        })
        .then(data => {
            if (Array.isArray(data)) {
                updateSelect(schedulerSelect, data);
                
                // Выбираем сохраненное значение, если оно существует в новом списке
                if (currentScheduler) {
                    const exists = Array.from(schedulerSelect.options).some(
                        option => option.value === currentScheduler
                    );
                    
                    if (exists) {
                        schedulerSelect.value = currentScheduler;
                    }
                }
            }
        })
        .catch(error => {
            console.error('Ошибка при загрузке планировщиков:', error);
        });
    
    // Обновляем список моделей SD
    fetch('/settings/api/sd-models')
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка получения списка моделей SD');
            }
            return response.json();
        })
        .then(data => {
            if (Array.isArray(data)) {
                updateSelect(sdModelSelect, data, 'title', 'title');
                
                // Выбираем сохраненное значение, если оно существует в новом списке
                if (currentSdModel) {
                    const exists = Array.from(sdModelSelect.options).some(
                        option => option.value === currentSdModel
                    );
                    
                    if (exists) {
                        sdModelSelect.value = currentSdModel;
                    }
                }
            }
        })
        .catch(error => {
            console.error('Ошибка при загрузке моделей SD:', error);
        });
}

// Ждем загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    const apiUrlInput = document.getElementById('api_url');
    
    if (apiUrlInput) {
        // При изменении URL API - обновляем списки
        apiUrlInput.addEventListener('change', updateSDParameters);
        
        // Кнопка для проверки соединения
        const checkConnectionBtn = document.getElementById('check_connection');
        if (checkConnectionBtn) {
            checkConnectionBtn.addEventListener('click', function(e) {
                e.preventDefault();
                updateSDParameters();
                // Тут можно добавить дополнительную логику проверки соединения
                alert('Обновляем списки параметров с API Stable Diffusion');
            });
        }
    }
}); 