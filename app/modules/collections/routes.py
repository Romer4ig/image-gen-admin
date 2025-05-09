from flask import render_template, request, url_for, redirect, flash, jsonify
from sqlalchemy import distinct
from app.modules.collections import collections_bp
from app.models import Collection, Project, GenerationTask, db, Favorite
from app.modules.collections.services import get_collection_projects, get_generation_status

@collections_bp.route('/')
def list_collections():
    """Страница со списком коллекций"""
    # Получаем параметр фильтрации по типу из URL
    type_filter = request.args.get('type', '')
    
    # Получаем все уникальные типы для фильтрации
    types = [t[0] for t in Collection.query.with_entities(distinct(Collection.type)).all()]
    # Получаем все проекты для фильтрации
    projects = Project.query.all()
    
    # Базовый запрос
    query = Collection.query
    
    # Фильтруем коллекции по типу, если параметр указан
    if type_filter:
        query = query.filter(Collection.type == type_filter)
    
    # Получаем коллекции
    all_collections = query.all()
    
    # Получаем информацию о проектах и статусах для каждой коллекции
    collection_projects = get_collection_projects(all_collections)
    generation_status = {}
    
    # Определяем статус генерации для пар коллекция-проект
    for collection in all_collections:
        for project in collection_projects.get(collection.id, []):
            key = f"{collection.id}-{project.id}"
            status = get_generation_status(collection.id, project.id)
            generation_status[key] = status
    
    # Передаем данные в шаблон вместе с информацией о текущем фильтре
    return render_template(
        'collections/list.html',
        collections=all_collections, 
        types=types,
        projects=projects,
        current_type=type_filter,
        total_count=Collection.query.count(),
        collection_projects=collection_projects,
        generation_status=generation_status
    )

@collections_bp.route('/<int:collection_id>/view')
def view_collection(collection_id):
    """Страница подробного просмотра коллекции с результатами генерации"""
    collection = Collection.query.get_or_404(collection_id)
    
    # Группируем задачи по проектам, берем только последнюю успешную задачу для каждого проекта
    projects_data = {}
    
    # Получаем все завершенные задачи для этой коллекции
    completed_tasks = GenerationTask.query.filter_by(
        collection_id=collection_id, 
        status='completed'
    ).order_by(GenerationTask.completed_at.desc()).all()
    
    # Получаем все избранные изображения
    favorites = {}
    for task in completed_tasks:
        task_favorites = Favorite.query.filter_by(task_id=task.id).all()
        if task_favorites:
            favorites[task.id] = [fav.image_path for fav in task_favorites]
    
    # Сгруппируем задачи по проектам и выберем последнюю для каждого проекта
    for task in completed_tasks:
        project = Project.query.get(task.project_id)
        if project and project.id not in projects_data:
            projects_data[project.id] = {
                'project': project,
                'task': task,
                'favorites': favorites.get(task.id, [])
            }
    
    return render_template(
        'collections/view.html',
        collection=collection,
        projects_data=projects_data
    )

@collections_bp.route('/update_prompt', methods=['POST'])
def update_prompt():
    """Обновление промпта коллекции"""
    data = request.json
    
    if not data or 'collection_id' not in data:
        return jsonify({'success': False, 'error': 'Неполные данные'}), 400
    
    try:
        collection_id = int(data['collection_id'])
        collection = Collection.query.get(collection_id)
        
        if not collection:
            return jsonify({'success': False, 'error': f'Коллекция с ID {collection_id} не найдена'}), 404
        
        # Обновляем обычный промпт, если он предоставлен
        if 'prompt' in data:
            collection.prompt = data['prompt']
            
        # Обновляем негативный промпт, если он предоставлен
        if 'negative_prompt' in data:
            collection.negative_prompt = data['negative_prompt']
            
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@collections_bp.route('/create', methods=['POST'])
def create_collection():
    """Создание новой коллекции"""
    try:
        collection_id = request.form.get('id')
        title = request.form.get('title')
        collection_type = request.form.get('type')
        
        if not collection_id or not title or not collection_type:
            flash('ID, название и тип коллекции обязательны для заполнения', 'error')
            return redirect(url_for('collections.list_collections'))
            
        # Проверяем, не существует ли уже коллекция с таким ID
        existing_collection = Collection.query.get(collection_id)
        if existing_collection:
            flash(f'Коллекция с ID {collection_id} уже существует', 'error')
            return redirect(url_for('collections.list_collections'))
        
        collection = Collection(
            id=collection_id,
            title=title,
            type=collection_type
        )
        
        db.session.add(collection)
        db.session.commit()
        
        flash('Коллекция успешно создана', 'success')
        return redirect(url_for('collections.list_collections'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при создании коллекции: {str(e)}', 'error')
        return redirect(url_for('collections.list_collections'))
