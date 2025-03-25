from app.models import Project, GenerationTask

def get_project_task_stats(project_id):
    """
    Получает статистику задач для проекта
    
    Args:
        project_id: ID проекта
        
    Returns:
        dict: Словарь со статистикой задач
    """
    # Общее количество задач для проекта
    total_tasks = GenerationTask.query.filter_by(project_id=project_id).count()
    
    # Количество завершенных задач
    completed_tasks = GenerationTask.query.filter_by(
        project_id=project_id, 
        status='completed'
    ).count()
    
    # Количество задач в обработке
    processing_tasks = GenerationTask.query.filter_by(
        project_id=project_id
    ).filter(GenerationTask.status.in_(['pending', 'processing'])).count()
    
    # Количество задач с ошибкой
    failed_tasks = GenerationTask.query.filter_by(
        project_id=project_id,
        status='failed'
    ).count()
    
    return {
        'total': total_tasks,
        'completed': completed_tasks,
        'processing': processing_tasks,
        'failed': failed_tasks
    }
