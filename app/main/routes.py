from flask import render_template, request, url_for, redirect, flash, jsonify
from app.main import main_bp
from app.models import Collection, Project, GenerationTask, db
from app.services.task_manager import task_manager
from sqlalchemy import distinct

@main_bp.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@main_bp.route('/collections')
def collections():
    """Страница со списком коллекций"""
    # Получаем параметр фильтрации по типу из URL
    type_filter = request.args.get('type', '')
    project_filter = request.args.get('project', '')
    
    # Получаем все уникальные типы для фильтрации
    types = [t[0] for t in Collection.query.with_entities(distinct(Collection.type)).all()]
    # Получаем все проекты для фильтрации
    projects = Project.query.all()
    
    # Базовый запрос
    query = Collection.query
    
    # Фильтруем коллекции по типу, если параметр указан
    if type_filter:
        query = query.filter(Collection.type == type_filter)
    
    # Фильтруем коллекции по проекту, если параметр указан
    if project_filter:
        # Получаем коллекции, которые имеют задачи с указанным проектом
        collection_ids = GenerationTask.query.filter_by(project_id=project_filter).with_entities(GenerationTask.collection_id).distinct().all()
        collection_ids = [cid[0] for cid in collection_ids]
        query = query.filter(Collection.id.in_(collection_ids))
    
    # Получаем коллекции
    all_collections = query.all()
    
    # Словарь для хранения проектов для каждой коллекции на основе выполненных задач
    collection_projects = {}
    # Информация о статусе генерации для каждой пары коллекция-проект
    generation_status = {}
    
    # Получаем все проекты с завершенными задачами для каждой коллекции
    for collection in all_collections:
        # Получаем все проекты с задачами для данной коллекции
        tasks = GenerationTask.query.filter_by(collection_id=collection.id).all()
        
        # Список проектов для данной коллекции
        collection_projects[collection.id] = []
        
        for task in tasks:
            if task.project_id and task.project_id not in [p.id for p in collection_projects[collection.id]]:
                project = Project.query.get(task.project_id)
                if project:
                    collection_projects[collection.id].append(project)
                    
                    # Определяем статус генерации для пары коллекция-проект
                    key = f"{collection.id}-{project.id}"
                    status = get_generation_status(collection.id, project.id)
                    generation_status[key] = status
    
    # Передаем данные в шаблон вместе с информацией о текущем фильтре
    return render_template(
        'collections.html',
        collections=all_collections, 
        types=types,
        projects=projects,
        current_type=type_filter,
        current_project=project_filter,
        total_count=Collection.query.count(),
        collection_projects=collection_projects,
        generation_status=generation_status
    )

def get_generation_status(collection_id, project_id):
    """
    Проверяет статус генерации для пары коллекция-проект
    
    Returns:
        str: 'completed' - есть завершенные задачи
             'pending' - есть ожидающие или выполняющиеся задачи
             'failed' - есть только задачи с ошибкой
             None - нет задач
    """
    # Проверяем наличие завершенных задач
    completed_task = GenerationTask.query.filter_by(
        collection_id=collection_id, 
        project_id=project_id,
        status='completed'
    ).first()
    
    if completed_task:
        return 'completed'
    
    # Проверяем наличие ожидающих или выполняющихся задач
    pending_task = GenerationTask.query.filter_by(
        collection_id=collection_id, 
        project_id=project_id
    ).filter(
        GenerationTask.status.in_(['pending', 'processing'])
    ).first()
    
    if pending_task:
        return 'pending'
    
    # Проверяем наличие задач с ошибкой
    failed_task = GenerationTask.query.filter_by(
        collection_id=collection_id, 
        project_id=project_id,
        status='failed'
    ).first()
    
    if failed_task:
        return 'failed'
    
    # Нет задач
    return None

@main_bp.route('/generate/<int:collection_id>/<int:project_id>', methods=['POST'])
def generate_image(collection_id, project_id):
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
                return redirect(url_for('main.collections'))
            
            return redirect(url_for('main.tasks'))
    
    # Создаем новую задачу
    task = task_manager.create_task(collection_id, project_id)
    
    if task:
        flash(f'Задача на генерацию "{collection.title}" с проектом "{project.title}" добавлена в очередь', 'success')
    else:
        flash('Ошибка при создании задачи', 'danger')
    
    # Проверяем, был ли указан параметр redirect_to
    redirect_to = request.args.get('redirect_to')
    if redirect_to == 'collection':
        return redirect(url_for('main.collections'))
    
    # По умолчанию перенаправляем на страницу задач
    return redirect(url_for('main.tasks'))

@main_bp.route('/batch-generate', methods=['POST'])
def batch_generate():
    """Пакетное создание задач на генерацию изображений"""
    # Получаем ID выбранных коллекций и проекта
    collection_ids = request.form.getlist('collection_ids')
    project_id = request.form.get('project_id')
    force_generation = 'force_generation' in request.form
    
    if not collection_ids or not project_id:
        flash('Необходимо выбрать хотя бы одну коллекцию и проект', 'danger')
        return redirect(url_for('main.collections'))
    
    project = Project.query.get_or_404(project_id)
    
    # Счетчики для сообщения
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    # Создаем задачи для каждой коллекции
    for collection_id in collection_ids:
        collection = Collection.query.get(collection_id)
        if collection:
            # Проверяем, существует ли уже задача в процессе выполнения
            if not force_generation:
                existing_task = GenerationTask.query.filter_by(
                    collection_id=collection_id,
                    project_id=project_id
                ).first()
                
                if existing_task:
                    # Пропускаем, так как задача уже существует
                    skipped_count += 1
                    continue
            
            # Создаем задачу
            task = task_manager.create_task(collection_id, project_id)
            
            if task:
                created_count += 1
            else:
                error_count += 1
    
    # Формируем сообщение о результате
    if created_count > 0:
        flash(f'Создано {created_count} задач на генерацию с проектом "{project.title}"', 'success')
    
    if skipped_count > 0:
        flash(f'Пропущено {skipped_count} коллекций с существующими задачами', 'info')
    
    if error_count > 0:
        flash(f'Не удалось создать {error_count} задач', 'warning')
    
    if created_count == 0 and error_count == 0 and skipped_count == 0:
        flash('Не создано ни одной новой задачи.', 'info')
    
    return redirect(url_for('main.tasks'))

@main_bp.route('/tasks')
def tasks():
    """Страница со списком задач генерации"""
    # Получаем параметры из запроса
    status_filter = request.args.get('status', '')
    collection_id = request.args.get('collection_id')
    project_id = request.args.get('project_id')
    
    # Базовый запрос
    query = GenerationTask.query
    
    # Фильтрация по статусу
    if status_filter:
        query = query.filter(GenerationTask.status == status_filter)
    
    # Фильтрация по коллекции
    if collection_id:
        query = query.filter(GenerationTask.collection_id == collection_id)
        
    # Фильтрация по проекту
    if project_id:
        query = query.filter(GenerationTask.project_id == project_id)
    
    # Сортировка по времени создания (сначала новые)
    tasks = query.order_by(GenerationTask.created_at.desc()).all()
    
    # Получаем связанные данные для отображения в фильтрах
    collections = Collection.query.all()
    projects = Project.query.all()
    
    return render_template(
        'tasks.html',
        tasks=tasks,
        status_filter=status_filter,
        collection_id=collection_id,
        project_id=project_id,
        collections=collections,
        projects=projects
    )

@main_bp.route('/tasks/<int:task_id>')
def task_detail(task_id):
    """Страница с детальной информацией о задаче"""
    task = GenerationTask.query.get_or_404(task_id)
    return render_template('task_detail.html', task=task)

@main_bp.route('/projects')
def projects():
    """Страница со списком проектов"""
    all_projects = Project.query.all()
    return render_template('projects.html', projects=all_projects)

@main_bp.route('/projects/add', methods=['GET', 'POST'])
def add_project():
    """Добавление нового проекта"""
    if request.method == 'POST':
        title = request.form.get('title')
        basic_prompt = request.form.get('basic_prompt')
        
        if title:
            project = Project(title=title, basic_prompt=basic_prompt)
            db.session.add(project)
            db.session.commit()
            flash('Проект успешно создан', 'success')
            return redirect(url_for('main.projects'))
        else:
            flash('Необходимо указать название проекта', 'danger')
    
    return render_template('project_form.html')

@main_bp.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    """Редактирование проекта"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        basic_prompt = request.form.get('basic_prompt')
        
        if title:
            project.title = title
            project.basic_prompt = basic_prompt
            db.session.commit()
            flash('Проект успешно обновлен', 'success')
            return redirect(url_for('main.projects'))
        else:
            flash('Необходимо указать название проекта', 'danger')
    
    return render_template('project_form.html', project=project) 