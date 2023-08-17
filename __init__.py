from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user

db = SQLAlchemy()
DB_NAME = "database.db"

from views import views
from os import path

def create_app():
    app = Flask(__name__)
    app.register_blueprint(views, url_prefix="/")
    app.config['SECRET_KEY'] = 'aoufhbwiufgyavbigfa'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from models import Member

    with app.app_context():
        if not path.exists('instance/' + DB_NAME):
            db.create_all()
            print('Created Database!')

    login_manager = LoginManager()
    login_manager.login_view = 'views.home'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Member.query.get(int(id))

    return app
