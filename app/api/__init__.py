from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import routes
from app.api import routes
