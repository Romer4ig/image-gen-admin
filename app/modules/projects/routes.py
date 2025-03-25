from flask import render_template, request, url_for, redirect, flash
from app.modules.projects import projects_bp
from app.models import Project, db

@projects_bp.route('/')
def list_projects():
    """Страница со списком проектов"""
    projects = Project.query.all()
    return render_template('projects/list.html', projects=projects)

@projects_bp.route('/create', methods=['GET', 'POST'])
def create_project():
    """Создание нового проекта"""
    if request.method == 'POST':
        title = request.form.get('title')
        basic_prompt = request.form.get('basic_prompt', '')
        
        if not title:
            flash('Название проекта обязательно', 'danger')
        else:
            # Создаем новый проект
            project = Project(title=title, basic_prompt=basic_prompt)
            db.session.add(project)
            db.session.commit()
            
            flash(f'Проект "{title}" успешно создан', 'success')
            return redirect(url_for('projects.list_projects'))
    
    return render_template('projects/create.html')

@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Редактирование проекта"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        basic_prompt = request.form.get('basic_prompt', '')
        
        if not title:
            flash('Название проекта обязательно', 'danger')
        else:
            # Обновляем проект
            project.title = title
            project.basic_prompt = basic_prompt
            db.session.commit()
            
            flash(f'Проект "{title}" успешно обновлен', 'success')
            return redirect(url_for('projects.list_projects'))
    
    return render_template('projects/edit.html', project=project)
