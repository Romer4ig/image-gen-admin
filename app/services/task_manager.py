from app.models import db, GenerationTask, Collection, Project, Settings
from app.services.image_generator import ImageGenerator
from datetime import datetime
import threading
import time
import logging
from contextlib import nullcontext

logger = logging.getLogger(__name__)

class TaskManager:
    """Менеджер задач для генерации изображений"""
    
    def __init__(self, app=None):
        self.app = app
        self.worker_thread = None
        self.stop_worker = False
        self.generator = ImageGenerator()
    
    def create_generation_task(self, collection_id, project_id):
        """
        Создает новую задачу для генерации изображений
        
        Args:
            collection_id: ID коллекции
            project_id: ID проекта
            
        Returns:
            task: Созданная задача
        """
        # Получаем коллекцию и проект
        collection = Collection.query.get(collection_id)
        project = Project.query.get(project_id)
        
        if not collection or not project:
            return None
        
        # Формируем промпт из basic_prompt проекта и промпта коллекции
        prompt = ""
        if project.basic_prompt:
            prompt += project.basic_prompt.strip()
        
        if collection.prompt:
            if prompt:
                prompt += ", "
            prompt += collection.prompt.strip()
            
        # Создаем новую задачу
        task = GenerationTask(
            prompt=prompt,
            collection_id=collection_id,
            project_id=project_id,
            status='pending'
        )
        
        db.session.add(task)
        db.session.commit()
        
        # Запускаем обработчик задач, если он еще не запущен
        self.ensure_worker_running()
        
        return task
    
    def start_worker(self):
        """Запускает фоновый поток для обработки задач"""
        if self.worker_thread and self.worker_thread.is_alive():
            return
            
        self.stop_worker = False
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("Worker thread started")
    
    def stop_worker(self):
        """Останавливает фоновый поток"""
        self.stop_worker = True
        if self.worker_thread:
            self.worker_thread.join(timeout=3.0)
    
    def ensure_worker_running(self):
        """Проверяет, запущен ли воркер, и запускает его при необходимости"""
        if not self.worker_thread or not self.worker_thread.is_alive():
            self.start_worker()
    
    def _worker_loop(self):
        """Основной цикл обработки задач"""
        # Проверяем наличие контекста приложения
        if self.app:
            context_manager = self.app.app_context()
        else:
            # Используем пустой контекст, если приложение не определено
            context_manager = nullcontext()
            
        with context_manager:
            while not self.stop_worker:
                try:
                    # Получаем следующую задачу со статусом 'pending'
                    task = GenerationTask.query.filter_by(status='pending').order_by(GenerationTask.created_at).first()
                    
                    if task:
                        # Обновляем статус и время начала
                        task.status = 'processing'
                        task.started_at = datetime.utcnow()
                        db.session.commit()
                        
                        try:
                            # Генерируем изображение (всегда как batch)
                            result = self.generator.generate_image(task.prompt)

                            # Обновляем задачу с результатом
                            if result['success']:
                                task.status = 'completed'
                                
                                # Сохраняем основной путь к изображению (для обратной совместимости)
                                task.result_path = result['path']
                                
                                # Сохраняем все пути через разделитель для поддержки нескольких изображений
                                if result.get('paths'):
                                    task.result_paths = ';'.join(result['paths'])
                                    task.batch_count = result['count']
                            else:
                                task.status = 'failed'
                                task.error = result.get('error', 'Неизвестная ошибка')
                                
                        except Exception as e:
                            logger.exception(f"Error processing task {task.id}")
                            task.status = 'failed'
                            task.error = str(e)
                        
                        # Обновляем время завершения
                        task.completed_at = datetime.utcnow()
                        db.session.commit()
                    else:
                        # Если нет задач, ждем некоторое время
                        time.sleep(1)
                        
                except Exception as e:
                    logger.exception("Error in worker loop")
                    time.sleep(5)  # Пауза в случае ошибки
        
        logger.info("Worker thread stopped")

# Создаем глобальный экземпляр менеджера задач
task_manager = TaskManager()

def init_app(app):
    """Инициализирует менеджер задач с приложением Flask"""
    global task_manager
    task_manager.app = app
    
    # Запускаем воркер при необходимости
    task_manager.ensure_worker_running()