from app.auth.forms import EmptyForm
from flask import render_template, url_for, jsonify
from app.activity import bp
from flask_login import login_required
from app import db
from datetime import datetime
from app.models import Activity, User
from app.main.forms import EmptyForm


@bp.route('/activity-list', methods=['GET', 'POST'])
@login_required
def activity_list():
    """
    Renders Activity page
    """
    form=EmptyForm()
    return render_template('activity_list.html', title='Activity-List', route="activity", form=form)


@bp.route('/ajax-activity-list', methods=['GET'])
@login_required
def ajax_activity_list():
    """
    Ajax request to render Activity list table
    """
    date_format = '%d.%m.%Y:%H:%M:%S'
    data = [
        [
            a.id, datetime.strftime(a.last, date_format), a.action, a.user
        ] for a in db.session.query(Activity).all()]
    response = {'data': data}
    return jsonify(response)
