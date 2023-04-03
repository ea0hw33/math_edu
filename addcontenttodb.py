from edu_lite import db, app
from edu_lite.models import *


def AddContent(app):
    db.session.add(Topics(name='Сложение и вычитание'))
    db.session.add(Topics(name='-'))


if __name__ == "__main__":
    with app.app_context():
        AddContent(app)