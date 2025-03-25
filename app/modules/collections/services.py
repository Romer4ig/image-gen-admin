from app.models import GenerationTask, Project

def get_collection_projects(collections):
    """
    Получает словарь проектов для списка коллекций
    
    Args:
        collections: Список коллекций
        
    Returns:
        dict: Словарь {collection_id: [project1, project2, ...]}
    """
    collection_projects = {}
    
    # Получаем все проекты
    all_projects = Project.query.all()
    
    for collection in collections:
        # Добавляем все проекты для каждой коллекции
        collection_projects[collection.id] = all_projects
    
    return collection_projects

def get_generation_status(collection_id, project_id):
    """
    Проверяет статус генерации для пары коллекция-проект
    
    Args:
        collection_id: ID коллекции
        project_id: ID проекта
        
    Returns:
        str: 'completed' - есть завершенные задачи
             'pending' - есть ожидающие или выполняющиеся задачи
             'failed' - есть только задачи с ошибкой
             None - нет задач
    """
    # Проверяем наличие завершенных задач
    completed_task = GenerationTask.query.filter_by(
        collection_id=collection_id, 
        project_id=project_id,
        status='completed'
    ).first()
    
    if completed_task:
        return 'completed'
    
    # Проверяем наличие ожидающих или выполняющихся задач
    pending_task = GenerationTask.query.filter_by(
        collection_id=collection_id, 
        project_id=project_id
    ).filter(GenerationTask.status.in_(['pending', 'processing'])).first()
    
    if pending_task:
        return 'pending'
    
    # Проверяем наличие задач с ошибкой
    failed_task = GenerationTask.query.filter_by(
        collection_id=collection_id, 
        project_id=project_id,
        status='failed'
    ).first()
    
    if failed_task:
        return 'failed'
    
    # Если нет задач
    return None
