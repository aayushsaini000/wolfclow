from flask import Blueprint

bp = Blueprint('activity', __name__)

from app.activity import routes
