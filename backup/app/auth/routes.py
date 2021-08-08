from flask import render_template, redirect, url_for, flash, request, jsonify
from sqlalchemy.sql.expression import delete
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import CreateUserForm, LoginForm, EmptyForm
from app.models import User
from sqlalchemy.sql import func
from datetime import datetime


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Renders login page and redirects to dashboard after successfull login
    """
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        # update last_login column value
        user.last_login = func.now()
        db.session.commit()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    """
    Performs user logout and redirects to login
    """
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/user-list', methods=['GET'])
@login_required
def user_list():
    """
    Renders User list page
    """
    form = EmptyForm(request.form)
    user_form = CreateUserForm(request.form)
    return render_template('user_list.html', title='User-List', route="user", form=form,
    user_form=user_form)


@bp.route('/user-delete/<int:pk>', methods=['POST'])
@login_required
def user_delete(pk):
    """
    Delete a user and redirect to User list page
    """
    form = EmptyForm(request.form)
    if request.method == 'POST' and form.validate():
        if User.query.filter_by(id=pk).first() is not None:
            user = User.query.get(pk)
            db.session.delete(user)
            db.session.commit()
        return redirect(url_for('auth.user_list'))


@bp.route('/ajax-user-create', methods=['POST'])
@login_required
def ajax_user_create():
    """
    Ajax request to create a new User
    """
    username = request.form.get('username')
    password = request.form.get('password')
    if User.find_user_by_username(username):
        msg = "Username already exists."
        status = "error"
    else:
        if User.find_user_by_username(username=username) is None:    
            usr = User.create_user(username=username, password=password)
        msg = "User created successfully."
        status = "success"
    return jsonify({'msg': msg, 'status': status})
    

@bp.route('/ajax-user-list', methods=['GET'])
@login_required
def ajax_user_list():
    """
    Ajax request render User table data
    """
    delete_action_html = """<a href="#" data-url="{}" 
    class="tableLinkDelete"><i class="material-icons">&#xE872;</i></a>"""
    date_format = '%d.%m.%Y:%H:%M:%S'
    data = [
        [
            u.id, u.username, datetime.strftime(u.created_at, date_format), 
            datetime.strftime(u.last_login, date_format) if u.last_login else None,
            delete_action_html.format(url_for('auth.user_delete', pk=u.id))
        ] for u in db.session.query(User).all()]
    return jsonify({'data': data})


@bp.route('/ajax-user-change-password', methods=['POST'])
@login_required
def ajax_user_change_password():
    """
    Ajax request changes User password
    """
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    if not current_user.check_password(current_password):
        msg = "Incorrect current password."
        status = "error"
    else:
        current_user.set_password(new_password)
        db.session.commit()
        msg = "Password updated successfully."
        status = "success"
    return jsonify({'msg': msg, 'status': status})
