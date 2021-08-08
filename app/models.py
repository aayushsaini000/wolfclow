from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from sqlalchemy.sql import func


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())
    last_login = db.Column(db.DateTime)
    events = db.relationship('Event', backref='user_events', lazy=True)
    activities = db.relationship('Activity', backref='user_activities', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Class method which finds user from DB by username
    @classmethod
    def find_user_by_username(cls, username):
        return User.query.filter_by(username=username).first()

    @classmethod
    def create_user(cls, **kw):
        obj = cls(**kw)
        username = obj.username
        
        if cls.find_user_by_username(username):
            raise ValueError("Username already exists.")
        
        user = User(username=username)
        user.set_password(obj.password)      
        db.session.add(user)
        db.session.commit()
        return user

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, server_default=func.now())
    activity = db.Column(db.String(255))
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, server_default=func.now())
    task_type = db.Column(db.String(50))
    command = db.Column(db.String(300))
    output = db.Column(db.Text)
    status = db.Column(db.String(20))
    guid = db.Column(db.String(100))
    computername = db.Column(db.String(100))
    file_input = db.Column(db.Text)

class loot(db.Model):
    __tablename__ = 'loot'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, server_default=func.now())
    type = db.Column(db.String(50))
    data = db.Column(db.Text)
    guid = db.Column(db.String(100))


class Host(db.Model):
    __tablename__ = 'host'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), index=True)
    computername = db.Column(db.String(100))
    country = db.Column(db.String(150))
    infection_date = db.Column(db.DateTime, server_default=func.now())
    last = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    status = db.Column(db.String(20))
    guid = db.Column(db.String(100))
    notes = db.Column(db.String(255))
    systeminfo = db.Column(db.String(255))
    open_connections = db.Column(db.String(255))
    arp_info = db.Column(db.String(255))
    network_info = db.Column(db.String(255))
    processes = db.Column(db.String(255))

class Activity(db.Model):
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), index=True)
    country = db.Column(db.String(150))
    infection_date = db.Column(db.DateTime, server_default=func.now())
    last = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    status = db.Column(db.String(20))
    guid = db.Column(db.String(100))
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100))
