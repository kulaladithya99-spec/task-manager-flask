from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
from .models import db, User, migrate
import os

load_dotenv()

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY']                  = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI']     = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view    = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth.routes      import auth
    from .tasks.routes     import tasks
    from .dashboard.routes import dashboard

    app.register_blueprint(auth,      url_prefix='/auth')
    app.register_blueprint(tasks,     url_prefix='/tasks')
    app.register_blueprint(dashboard)

    with app.app_context():
        db.create_all()

    # 404 error handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app