from flask import render_template, request
from app import db
from app.errors import bp
from app.main.forms import EmptyForm


@bp.app_errorhandler(404)
def not_found_error(error):
    form = EmptyForm()
    return render_template('404.html', form=form), 404


@bp.app_errorhandler(500)
def internal_error(error):
    form = EmptyForm()
    db.session.rollback()
    return render_template('500.html', form=form), 500
