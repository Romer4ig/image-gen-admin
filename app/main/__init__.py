from flask import Blueprint

main_bp = Blueprint('main', __name__)

# Import routes
from app.main import routes 