from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from app.models import User
from flask import request
from wtforms.validators import ValidationError


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def validate_username(form, username):
        if len(username.data) < 5:
            raise ValidationError("Username must be atleast 5 characters long.")
        if User.find_user_by_username(username.data):
            print('username already exists')
            raise ValidationError("Username already exists.")

    def validate_password(form, password):
        if len(password.data) < 8:
            raise ValidationError("Password must be atleast 8 characters long.")        


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
