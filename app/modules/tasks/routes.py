from flask import render_template, request, url_for, redirect, flash, jsonify, abort
from app.modules.tasks import tasks_bp
from app.models import GenerationTask, Collection, Project, db, Settings, Favorite
from app.services.task_manager import task_manager
from app.modules.tasks.services import filter_tasks, get_task_details, batch_generate_tasks

@tasks_bp.route('/')
def list_tasks():
    """Отображает список задач генерации изображений"""
    status_filter = request.args.get('status')
    collection_id = request.args.get('collection_id')
    project_id = request.args.get('project_id')
    
    # Получаем настройки для пакетной генерации
    default_batch_size = Settings.get_setting('default_batch_size')
    max_batch_size = Settings.get_setting('max_batch_size')
    
    # Базовый запрос
    query = GenerationTask.query
    
    # Применяем фильтры
    if status_filter:
        query = query.filter(GenerationTask.status == status_filter)
    
    if collection_id:
        query = query.filter(GenerationTask.collection_id == collection_id)
    
    if project_id:
        query = query.filter(GenerationTask.project_id == project_id)
    
    # Получаем задачи (сортировка по дате создания)
    tasks = query.order_by(GenerationTask.created_at.desc()).all()
    
    # Получаем все коллекции и проекты для фильтров
    collections = Collection.query.all()
    projects = Project.query.all()
    
    return render_template(
        'tasks/list.html', 
        tasks=tasks, 
        status_filter=status_filter,
        collections=collections,
        projects=projects,
        collection_id=collection_id,
        project_id=project_id,
        default_batch_size=default_batch_size,
        max_batch_size=max_batch_size
    )

@tasks_bp.route('/<int:task_id>')
def view_task(task_id):
    """Просмотр деталей задачи"""
    task = GenerationTask.query.get_or_404(task_id)
    details = get_task_details(task)
    
    # Получаем выбранное изображение для этой задачи (если есть)
    selected_image = Favorite.query.filter_by(task_id=task_id).first()
    
    # Получаем все избранные изображения для этой задачи
    favorite_images = [fav.image_path for fav in Favorite.query.filter_by(task_id=task_id).all()]
    
    return render_template(
        'tasks/view.html', 
        task=task, 
        details=details, 
        selected_image=selected_image,
        favorite_images=favorite_images
    )

@tasks_bp.route('/select-image/<int:task_id>', methods=['POST'])
def select_image(task_id):
    """Выбор финального изображения для задачи"""
    task = GenerationTask.query.get_or_404(task_id)
    image_path = request.json.get('image_path')
    
    if not image_path:
        return jsonify({'success': False, 'error': 'Не указан путь к изображению'}), 400
    
    # Удаляем предыдущие выборы для этой задачи
    Favorite.query.filter_by(task_id=task_id).delete()
    
    # Создаем новую запись о выборе
    favorite = Favorite(task_id=task_id, image_path=image_path)
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify({'success': True})

@tasks_bp.route('/unselect-image/<int:task_id>', methods=['POST'])
def unselect_image(task_id):
    """Отмена выбора изображения для задачи"""
    Favorite.query.filter_by(task_id=task_id).delete()
    db.session.commit()
    
    return jsonify({'success': True})

@tasks_bp.route('/final-images')
def view_final_images():
    """Просмотр всех финальных изображений с фильтрацией"""
    collection_id = request.args.get('collection_id')
    project_id = request.args.get('project_id')
    
    # Базовый запрос для получения выбранных изображений
    query = db.session.query(
        Favorite,
        GenerationTask,
        Collection,
        Project
    ).join(
        GenerationTask,
        GenerationTask.id == Favorite.task_id
    ).join(
        Collection,
        Collection.id == GenerationTask.collection_id
    ).join(
        Project,
        Project.id == GenerationTask.project_id
    )
    
    # Применяем фильтры
    if collection_id:
        query = query.filter(GenerationTask.collection_id == collection_id)
    
    if project_id:
        query = query.filter(GenerationTask.project_id == project_id)
    
    # Получаем данные
    favorites = query.order_by(GenerationTask.collection_id, GenerationTask.project_id).all()
    
    # Группируем по коллекциям и проектам
    grouped_data = {}
    for fav, task, collection, project in favorites:
        if collection.id not in grouped_data:
            grouped_data[collection.id] = {
                'collection': collection,
                'projects': {}
            }
        
        if project.id not in grouped_data[collection.id]['projects']:
            grouped_data[collection.id]['projects'][project.id] = {
                'project': project,
                'image': fav.image_path
            }
    
    # Получаем все коллекции и проекты для фильтров
    collections = Collection.query.all()
    projects = Project.query.all()
    
    return render_template(
        'tasks/final_images.html',
        grouped_data=grouped_data,
        collections=collections,
        projects=projects,
        current_collection_id=collection_id,
        current_project_id=project_id
    )

@tasks_bp.route('/generate/<int:collection_id>/<int:project_id>', methods=['POST'])
def generate_task(collection_id, project_id):
    """Создание задачи на генерацию изображения"""
    collection = Collection.query.get_or_404(collection_id)
    project = Project.query.get_or_404(project_id)
    force_generation = 'force_generation' in request.form
    
    # Проверяем, есть ли уже активная задача для этой пары коллекция-проект
    if not force_generation:
        existing_task = GenerationTask.query.filter_by(
            collection_id=collection_id,
            project_id=project_id
        ).first()
        
        if existing_task:
            flash(f'Для коллекции "{collection.title}" и проекта "{project.title}" уже существует активная задача', 'warning')
            
            # Проверяем, был ли указан параметр redirect_to
            redirect_to = request.args.get('redirect_to')
            if redirect_to == 'collection':
                return redirect(url_for('collections.list_collections'))
            
            return redirect(url_for('tasks.list_tasks'))
    
    # Создаем новую задачу
    task = task_manager.create_generation_task(collection_id, project_id)
    
    if task:
        flash(f'Задача на генерацию "{collection.title}" с проектом "{project.title}" добавлена в очередь', 'success')
    else:
        flash('Ошибка при создании задачи', 'danger')
    
    # Проверяем, был ли указан параметр redirect_to
    redirect_to = request.args.get('redirect_to')
    if redirect_to == 'collection':
        return redirect(url_for('collections.list_collections'))
    
    # По умолчанию перенаправляем на страницу задач
    return redirect(url_for('tasks.list_tasks'))

@tasks_bp.route('/batch-generate', methods=['POST'])
def batch_generate():
    """Пакетное создание задач на генерацию изображений"""
    # Получаем ID выбранных коллекций и проекта
    collection_ids = request.form.getlist('collection_ids')
    project_id = request.form.get('project_id')
    force_generation = 'force_generation' in request.form
    
    if not collection_ids or not project_id:
        flash('Необходимо выбрать хотя бы одну коллекцию и проект', 'danger')
        return redirect(url_for('collections.list_collections'))
    
    # Выполняем пакетную генерацию задач
    result = batch_generate_tasks(collection_ids, project_id, force_generation)
    
    # Обрабатываем результаты
    if result['created'] > 0:
        flash(f'Создано {result["created"]} задач на генерацию с проектом "{result["project_title"]}"', 'success')
    
    if result['skipped'] > 0:
        flash(f'Пропущено {result["skipped"]} коллекций с существующими задачами', 'info')
    
    if result['errors'] > 0:
        flash(f'Не удалось создать {result["errors"]} задач', 'warning')
    
    if result['created'] == 0 and result['errors'] == 0 and result['skipped'] == 0:
        flash('Не создано ни одной новой задачи.', 'info')
    
    return redirect(url_for('tasks.list_tasks'))