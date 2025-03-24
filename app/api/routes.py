from flask import jsonify, request
from app.api import api_bp
from app.models import db, Collection, GenerationTask

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@api_bp.route('/collections', methods=['GET'])
def get_collections():
    collections = Collection.query.all()
    result = []
    
    for collection in collections:
        result.append({
            'id': collection.id,
            'title': collection.title,
            'type': collection.type,
            'prompt': collection.prompt
        })
    
    return jsonify(result)

@api_bp.route('/collections/<int:collection_id>', methods=['GET'])
def get_collection(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    
    return jsonify({
        'id': collection.id,
        'title': collection.title,
        'type': collection.type,
        'prompt': collection.prompt
    })

@api_bp.route('/pending-tasks-count', methods=['GET'])
def pending_tasks_count():
    """Возвращает количество задач в статусе 'pending' и 'processing'"""
    count = GenerationTask.query.filter(
        GenerationTask.status.in_(['pending', 'processing'])
    ).count()
    
    return jsonify({
        'count': count
    })

@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Возвращает список задач"""
    status = request.args.get('status')
    
    query = GenerationTask.query
    
    if status:
        query = query.filter(GenerationTask.status == status)
    
    tasks = query.order_by(GenerationTask.created_at.desc()).all()
    
    result = [task.to_dict() for task in tasks]
    
    return jsonify(result)

@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Возвращает информацию о конкретной задаче"""
    task = GenerationTask.query.get_or_404(task_id)
    
    return jsonify(task.to_dict()) 