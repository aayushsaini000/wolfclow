from flask import render_template, url_for, jsonify, redirect, request
from app.task import bp
from flask_login import login_required
from app.main.forms import EmptyForm
#from app.models import Loot
from app import db
from datetime import datetime
from app import csrf
import base64


