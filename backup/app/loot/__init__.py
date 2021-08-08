from flask import Blueprint

bp = Blueprint('loot', __name__)

from app.loot import routes
