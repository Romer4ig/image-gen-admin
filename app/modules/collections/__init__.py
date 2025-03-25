from flask import Blueprint

collections_bp = Blueprint('collections', __name__, url_prefix='/collections')

from app.modules.collections import routes
