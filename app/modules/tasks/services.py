from app.models import GenerationTask, Collection, Project
from app.services.task_manager import task_manager

def filter_tasks(status_filter=None, collection_id=None, project_id=None):
    """
    Фильтрует задачи по заданным параметрам
    
    Args:
        status_filter: Фильтр по статусу задачи
        collection_id: ID коллекции
        project_id: ID проекта
        
    Returns:
        list: Отфильтрованный список задач
    """
    # Базовый запрос
    query = GenerationTask.query
    
    # Фильтрация по статусу
    if status_filter:
        query = query.filter(GenerationTask.status == status_filter)
    
    # Фильтрация по коллекции
    if collection_id:
        query = query.filter(GenerationTask.collection_id == collection_id)
        
    # Фильтрация по проекту
    if project_id:
        query = query.filter(GenerationTask.project_id == project_id)
    
    # Сортировка по времени создания (сначала новые)
    return query.order_by(GenerationTask.created_at.desc()).all()

def get_task_details(task):
    """
    Получает детали задачи, включая связанные сущности
    
    Args:
        task: Объект задачи
        
    Returns:
        dict: Словарь с дополнительной информацией о задаче
    """
    details = {
        'collection': Collection.query.get(task.collection_id) if task.collection_id else None,
        'project': Project.query.get(task.project_id) if task.project_id else None,
        'duration': None
    }
    
    # Вычисляем длительность выполнения задачи, если она завершена
    if task.started_at and task.completed_at:
        duration = task.completed_at - task.started_at
        details['duration'] = {
            'seconds': duration.total_seconds(),
            'formatted': str(duration).split('.')[0]  # Формат ЧЧ:ММ:СС
        }
    
    return details

def batch_generate_tasks(collection_ids, project_id, force_generation=False):
    """
    Выполняет пакетную генерацию задач для указанных коллекций и проекта
    
    Args:
        collection_ids: Список ID коллекций
        project_id: ID проекта
        force_generation: Флаг принудительной генерации
        
    Returns:
        dict: Результаты создания задач
    """
    project = Project.query.get(project_id)
    
    if not project:
        return {
            'created': 0,
            'skipped': 0,
            'errors': len(collection_ids),
            'project_title': 'Неизвестный проект'
        }
    
    # Счетчики для сообщения
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    # Создаем задачи для каждой коллекции
    for collection_id in collection_ids:
        collection = Collection.query.get(collection_id)
        if collection:
            # Проверяем, существует ли уже задача в процессе выполнения
            if not force_generation:
                existing_task = GenerationTask.query.filter_by(
                    collection_id=collection_id,
                    project_id=project_id
                ).first()
                
                if existing_task:
                    # Пропускаем, так как задача уже существует
                    skipped_count += 1
                    continue
            
            # Создаем задачу
            task = task_manager.create_generation_task(collection_id, project_id)
            
            if task:
                created_count += 1
            else:
                error_count += 1
    
    return {
        'created': created_count,
        'skipped': skipped_count,
        'errors': error_count,
        'project_title': project.title
    }
