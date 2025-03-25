"""
Views для модуля задач - вспомогательные функции для формирования представлений
"""

def format_task_row(task, collection=None, project=None):
    """
    Форматирует данные задачи для отображения в таблице
    
    Args:
        task: Объект задачи
        collection: Объект связанной коллекции
        project: Объект связанного проекта
        
    Returns:
        dict: Форматированные данные задачи
    """
    collection_title = collection.title if collection else "Неизвестная коллекция"
    project_title = project.title if project else "Неизвестный проект"
    
    return {
        'id': task.id,
        'prompt': task.prompt,
        'status': task.status,
        'collection': {
            'id': task.collection_id,
            'title': collection_title
        },
        'project': {
            'id': task.project_id,
            'title': project_title
        },
        'created_at': task.created_at,
        'started_at': task.started_at,
        'completed_at': task.completed_at,
        'result_path': task.result_path,
        'error': task.error
    }
