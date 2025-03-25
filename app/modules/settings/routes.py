from flask import render_template, request, redirect, url_for, flash, jsonify
from app.modules.settings import settings_bp
from app.models import db, Settings
from app.services.image_generator import ImageGenerator


@settings_bp.route('/', methods=['GET', 'POST'])
def manage_settings():
    """Управление настройками приложения"""
    if request.method == 'POST':
        # Список всех настроек, которые могут быть в форме
        setting_keys = [
            'api_url',
            'default_batch_size',
            'max_batch_size', 
            'default_width',
            'default_height',
            'default_guidance_scale',
            'default_num_inference_steps',
            'default_sampler_name',
            'default_scheduler',
            'default_sd_model'
        ]
        
        # Сохраняем каждую настройку
        for key in setting_keys:
            if key in request.form:
                value = request.form[key]
                
                # Преобразуем числовые значения в соответствующие типы
                if key in ['default_batch_size', 'max_batch_size', 'default_width', 'default_height', 'default_num_inference_steps']:
                    value = int(value)
                elif key in ['default_guidance_scale']:
                    value = float(value)
                
                # Сохраняем настройку
                Settings.set_setting(key, value)
        
        flash('Настройки успешно сохранены', 'success')
        return redirect(url_for('settings.manage_settings'))
    
    # Для GET-запроса просто показываем форму с текущими настройками
    current_settings = Settings.get_all_settings()
    
    # Получаем списки семплеров и планировщиков из API
    image_generator = ImageGenerator()
    samplers = image_generator.get_samplers()
    schedulers = image_generator.get_schedulers()
    sd_models = image_generator.get_sd_models()
    
    return render_template(
        'settings/manage.html', 
        settings=current_settings,
        samplers=samplers,
        schedulers=schedulers,
        sd_models=sd_models
    )

@settings_bp.route('/api/samplers', methods=['GET'])
def get_samplers():
    """Возвращает список доступных семплеров из API"""
    try:
        image_generator = ImageGenerator()
        samplers = image_generator.get_samplers()
        return jsonify(samplers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@settings_bp.route('/api/schedulers', methods=['GET'])
def get_schedulers():
    """Возвращает список доступных планировщиков из API"""
    try:
        image_generator = ImageGenerator()
        schedulers = image_generator.get_schedulers()
        return jsonify(schedulers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@settings_bp.route('/api/sd-models', methods=['GET'])
def get_sd_models():
    """Возвращает список доступных моделей SD из API"""
    try:
        image_generator = ImageGenerator()
        models = image_generator.get_sd_models()
        return jsonify(models)
    except Exception as e:
        return jsonify({"error": str(e)}), 500 