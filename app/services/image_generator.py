import requests
import base64
import os
from pathlib import Path
from datetime import datetime
from app.models import Settings


class ImageGenerator:
    """Сервис для генерации изображений через Stable Diffusion API"""
    
    def __init__(self):
        """Инициализация сервиса генерации изображений"""
        pass
    
    def get_api_url(self):
        """Получает URL API из настроек"""
        return Settings.get_setting('api_url')
    
    def get_samplers(self):
        """
        Получает список доступных семплеров из API Stable Diffusion
        
        Returns:
            list: Список доступных семплеров или пустой список в случае ошибки
        """
        try:
            api_url = self.get_api_url()
            response = requests.get(url=f'{api_url}/sdapi/v1/samplers')
            response.raise_for_status()
            
            samplers = response.json()
            return samplers
        except Exception as e:
            print(f"Ошибка при получении списка семплеров: {e}")
            return []
    
    def get_schedulers(self):
        """
        Получает список доступных планировщиков из API Stable Diffusion
        
        Returns:
            list: Список доступных планировщиков или пустой список в случае ошибки
        """
        try:
            api_url = self.get_api_url()
            response = requests.get(url=f'{api_url}/sdapi/v1/schedulers')
            response.raise_for_status()
            
            schedulers = response.json()
            return schedulers
        except Exception as e:
            print(f"Ошибка при получении списка планировщиков: {e}")
            return []
    
    def get_sd_models(self):
        """
        Получает список доступных моделей Stable Diffusion из API
        
        Returns:
            list: Список доступных моделей или пустой список в случае ошибки
        """
        try:
            api_url = self.get_api_url()
            response = requests.get(url=f'{api_url}/sdapi/v1/sd-models')
            response.raise_for_status()
            
            models = response.json()
            return models
        except Exception as e:
            print(f"Ошибка при получении списка моделей SD: {e}")
            return []
    
    def generate_image(self, prompt, negative_prompt=None):
        """
        Генерирует изображение на основе промпта
        
        Args:
            prompt (str): Текст промпта для генерации
            negative_prompt (str, optional): Негативный промпт для генерации
            
        Returns:
            dict: Результат запроса и пути к сохраненным изображениям
        """
        # Получаем настройки
        steps = Settings.get_setting('default_num_inference_steps')
        width = Settings.get_setting('default_width')
        height = Settings.get_setting('default_height')
        guidance_scale = Settings.get_setting('default_guidance_scale')
        sampler_name = Settings.get_setting('default_sampler_name')
        scheduler = Settings.get_setting('default_scheduler')
        sd_model = Settings.get_setting('default_sd_model')

        batch_size = Settings.get_setting('default_batch_size')
        
        # Базовые параметры
        payload = {
            "prompt": prompt,
            "steps": steps,
            "width": width,
            "height": height,
            "cfg_scale": guidance_scale,
            "batch_size": batch_size,
            "sampler_name": sampler_name,
            "scheduler": scheduler,
        }
        
        # Добавляем негативный промпт, если он указан
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        # Добавляем модель, если она задана
        if sd_model:
            payload["override_settings"] = {
                "sd_model_checkpoint": sd_model
            }

        try:
            # Получаем URL API
            api_url = self.get_api_url()
            
            # Отправляем запрос на API
            response = requests.post(url=f'{api_url}/sdapi/v1/txt2img', json=payload)
            response.raise_for_status()  # Проверяем на ошибки
            result = response.json()
            
            # Создаем директорию для сохранения изображений
            output_dir = Path(os.path.join('app', 'static', 'generated'))
            output_dir.mkdir(exist_ok=True, parents=True)
            
            # Сохраняем все изображения
            image_paths = []
            for i, image_base64 in enumerate(result['images']):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                current_path = output_dir / f"image_{timestamp}_{i}.png"
                
                # Сохраняем изображение
                with open(current_path, 'wb') as f:
                    f.write(base64.b64decode(image_base64))
                
                # Преобразуем путь в формат с прямыми слешами для совместимости
                image_paths.append(str(current_path).replace(os.sep, '/'))
            
            return {
                "success": True,
                "path": image_paths[0] if len(image_paths) == 1 else None,  # Для обратной совместимости
                "paths": image_paths,
                "count": len(image_paths),
                "response": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }