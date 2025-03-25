"""
Views для модуля коллекций - вспомогательные функции для формирования представлений
"""

def format_collection_card(collection, projects=None, status_info=None):
    """
    Форматирует данные коллекции для отображения в карточке
    
    Args:
        collection: Объект коллекции
        projects: Список связанных проектов
        status_info: Информация о статусе генерации
        
    Returns:
        dict: Форматированные данные коллекции
    """
    return {
        'id': collection.id,
        'title': collection.title,
        'type': collection.type,
        'prompt': collection.prompt,
        'projects': projects or [],
        'status_info': status_info or {}
    }
