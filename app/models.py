from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime,default =datetime.utcnow)

    tasks = db.relationship('Task',backref='owner',lazy=True,cascade="all, delete-orphan"   )
    categories = db.relationship('Category', backref='owner', lazy=True,cascade='all, delete-orphan')


    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'
    

class Category(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    tasks   = db.relationship('Task', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'
    


class Task(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text,        nullable=True)
    done        = db.Column(db.Boolean,     default=False)
    priority    = db.Column(db.String(10),  default='medium')
    due_date    = db.Column(db.Date,        nullable=True)
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)
    is_archived = db.Column(db.Boolean, default=False)

    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'),     nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    def __repr__(self):
        return f'<Task {self.title}>'

    @property
    def is_overdue(self):
        if self.due_date and not self.done:
            return self.due_date < datetime.utcnow().date()
        return False
    
