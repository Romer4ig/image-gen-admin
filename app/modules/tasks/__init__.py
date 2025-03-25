from flask import Blueprint

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

from app.modules.tasks import routes
