from flask import Blueprint

bp = Blueprint('checkin', __name__)

from app.checkin import routes
