from flask_login import UserMixin
from sqlalchemy.sql import func
from apps import db  # db will be initialized from the app factory

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Note {self.data}>'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    email = db.Column(db.String(150))
    password = db.Column(db.String(150))
    notes = db.relationship('Note')

    def __repr__(self):
        return f'<User {self.name}>'
