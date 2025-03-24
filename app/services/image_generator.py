import requests
import base64
import os
from pathlib import Path

class ImageGenerator:
    """Сервис для генерации изображений через Stable Diffusion API"""
    
    def __init__(self, api_url=None):
        """Инициализация сервиса с указанным URL API"""
        self.api_url = api_url or os.environ.get('SD_API_URL', 'http://127.0.0.1:7860')
    
    def generate_image(self, prompt, output_path=None, **kwargs):
        """
        Генерирует изображение на основе промпта
        
        Args:
            prompt (str): Текст промпта для генерации
            output_path (str, optional): Путь для сохранения изображения
            **kwargs: Дополнительные параметры для API
            
        Returns:
            dict: Результат запроса и путь к сохраненному изображению
        """
        # Базовые параметры
        payload = {
            "prompt": prompt,
            "steps": kwargs.get("steps", 22),
            "width": kwargs.get("width", 640),
            "height": kwargs.get("height", 640),
            "sampler_name": kwargs.get("sampler_name", "Euler a"),
            "scheduler": kwargs.get("scheduler", "Simple"),
            "cfg_scale": kwargs.get("cfg_scale", 7),
        }
        
        # Добавляем остальные переданные параметры
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        try:
            # Отправляем запрос на API
            response = requests.post(url=f'{self.api_url}/sdapi/v1/txt2img', json=payload)
            response.raise_for_status()  # Проверяем на ошибки
            result = response.json()
            
            # Если не указан путь для сохранения, создаем его на основе метки времени
            if not output_path:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path('app/static/generated')
                output_dir.mkdir(exist_ok=True, parents=True)
                output_path = output_dir / f"image_{timestamp}.png"
            
            # Сохраняем изображение
            with open(output_path, 'wb') as f:
                f.write(base64.b64decode(result['images'][0]))
            
            return {
                "success": True,
                "path": str(output_path),
                "response": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            } 