from flask import render_template, url_for, jsonify, redirect, request
from app.task import bp
from flask_login import login_required
from app.main.forms import EmptyForm
from app.models import Task, Host
from app import db
from datetime import datetime
from app import csrf
import base64
from time import sleep

@bp.route('/task-list', methods=['GET', 'POST'])
@login_required
def task_list():
    """
    Renders Task list page
    """
    form = EmptyForm()
    return render_template('task_list.html', title='Task-List', route="task", form=form)


@bp.route('/ajax-task-list', methods=['GET'])
@login_required
def ajax_task_list():
    """
    Ajax request to render Task list table
    """
    command = ""
    data = []
    status_html = """<span class="badge badge-{}">{}</span>"""
    output_html = "<div class='form-group'><textarea class='form-control' readonly rows='3'>{}</textarea></div>"
    action_html = """
    <a href="#" class="tableActionIcons viewTaskOutput" data-outputText="{}" title="View" 
        data-command="{}" data-toggle="tooltip">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="24" viewBox="0 0 24 24" fill="none" 
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
        class="feather feather-disc">
        <circle cx="12" cy="12" r="10"></circle>
        <circle cx="12" cy="12" r="3"></circle>
        </svg>
    </a>
    <a href="#" class="tableActionIcons" title="re-run" data-toggle="tooltip" style="padding-left:25px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
        stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" 
        class="feather feather-chrome">
        <circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="4"></circle>
        <line x1="21.17" y1="8" x2="12" y2="8"></line><line x1="3.95" y1="6.06" x2="8.54" y2="14"></line>
        <line x1="10.88" y1="21.94" x2="15.46" y2="14"></line>
        </svg>
    </a>
    <a href="#" data-url="{}" style="padding-left:25px;" class="tableActionIcons deleteTask" title="Delete">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" 
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
        class="feather feather-trash-2">
        <polyline points="3 6 5 6 21 6"></polyline>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        <line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line>
        </svg>
    </a>
    """
    out = ""
    date_format = '%d.%m.%Y:%H:%M:%S'
    for t in db.session.query(Task).all():
        if t.status == 'Executed':
            status = status_html.format('success', t.status)
        elif t.status == 'new':
            status =status_html.format('info', t.status)
        else:
            status = status_html.format('danger', t.status)
        if t.task_type == 'screenshot' and t.output != None:
            out = """<a href='#' data-featherlight='#base64image'><img style='display:block; width:200px' id='base64image'                 
                                       src='data:image/jpeg;base64, {}'/></a>""".format(t.output.decode('UTF-8'),t.output.decode('UTF-8'), t.output.decode('UTF-8'))
            command = t.task_type
        elif t.task_type == 'command':
            try:
                out = output_html.format(base64.b64decode(t.output).decode('UTF-8'))
                command = t.command
            except:
                command = "none"
                pass 
        data.append(
            [
                t.id, t.computername, t.guid, datetime.strftime(t.time, date_format), t.task_type, 
                status, action_html.format(out, command, url_for('task.task_delete', pk=t.id))
            ]
        )
    response = {'data': data}
    return jsonify(response)


@bp.route('/task-delete/<int:pk>', methods=['POST'])
@login_required
def task_delete(pk):
    """
    Delete a task and redirects to Task listing page
    """
    form = EmptyForm(request.form)
    if request.method == 'POST' and form.validate():
        obj = Task.query.get(pk)
        db.session.delete(obj)
        db.session.commit()
        return redirect(url_for('task.task_list'))


@bp.route('/task_view/<int:pk>', methods=['GET'])
@login_required
def task_view(pk):
    """
    Presents the output of a task back to the user
    """
    #form = EmptyForm(request.form)
    if request.method == 'GET':
        obj = Task.query.get(pk)
        result = obj.output
        return result


@bp.route('/new/<guid>', methods=['GET'])
def newtask(guid=None):
    """
    Sends new task to client
    """
    if request.method == 'GET':
        status = Host.query.filter_by(guid=guid).first()
        status.status = "Online"
        status.last = datetime.now()
        db.session.commit()
        objects = Task.query.filter_by(guid=guid, status ="new").all()
        results = [
            {
                "task_type": object.task_type,
                "argument": object.command,
                "task_id": object.id
            } for object in objects
        ]
        response = {"tasks": results}
        return jsonify(response)


@bp.route('/newupload/<guid>/<taskid>', methods=['POST'])
@csrf.exempt #disable csrf on this function
def receive_data(guid=None,taskid=None):
    """
    receives data from client and add it to database
    """
    if request.method == 'POST':
        #output = base64.b64decode(request.form.get('data'))
        #print(request.form.get('data'))
        output = request.get_data()
        obj = Task.query.get(taskid)
        obj.guid = guid
        obj.status = "Executed"
        obj.output = output
        db.session.commit()
        return "OK"
        

@bp.route('/screenshot/<int:pk>', methods=['POST'])
@login_required
def take_screenshot(pk):
    """
    Process screenshot action on client 
    """
    form = EmptyForm(request.form)
    if request.method == 'POST' and form.validate():
        obj = Host.query.get(pk)
        obj = Task(task_type="screenshot", guid=obj.guid, status="new")
        db.session.add(obj)
        db.session.commit()
        return redirect(url_for('main.index'))