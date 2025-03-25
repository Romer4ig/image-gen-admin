"""
Views для модуля проектов - вспомогательные функции для формирования представлений
"""

def format_project_card(project, stats=None):
    """
    Форматирует данные проекта для отображения в карточке
    
    Args:
        project: Объект проекта
        stats: Статистика задач для проекта
        
    Returns:
        dict: Форматированные данные проекта
    """
    return {
        'id': project.id,
        'title': project.title,
        'basic_prompt': project.basic_prompt,
        'stats': stats or {
            'total': 0,
            'completed': 0,
            'processing': 0,
            'failed': 0
        }
    }
