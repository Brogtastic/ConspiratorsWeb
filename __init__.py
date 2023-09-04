from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user
import itertools
import random

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

    from models import Member, AvailableRoom

    with app.app_context():
        if not path.exists('instance/' + DB_NAME):
            db.create_all()
            alphabet = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
            combinations = [''.join(combination) for combination in itertools.product(alphabet, repeat=4)]
            random.shuffle(combinations)
            for combo in combinations:
                new_room_code = AvailableRoom(code=combo, in_use=False)
                db.session.add(new_room_code)
            db.session.commit()
            print('Created Database!')

    login_manager = LoginManager()
    login_manager.login_view = 'views.home'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Member.query.get(int(id))

    return app
