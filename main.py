from __init__ import create_app, db
from models import Room

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.session.query(Room).delete()
        db.session.commit()
    app.run(debug = True, port=8080)