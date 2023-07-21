from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from views import views
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.register_blueprint(views, url_prefix="/")
    app.config['SECRET_KEY'] = 'aoufhbwiufgyavbigfa'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    import models

    with app.app_context():
        if not path.exists('instance/' + DB_NAME):
            db.create_all()
            print('Created Database!')

    return app
