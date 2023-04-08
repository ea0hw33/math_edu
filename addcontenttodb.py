from edu_lite import db, app
from edu_lite.models import *


def AddContent(app):
    db.session.add(Topics(name='Натуральные числа'))
    db.session.add(Topics(name='Целые числа'))
    db.session.add(Topics(name='Десятичные числа'))
    for i in range(1,4):
        db.session.add(Subtopics(topic_id=i, name='Сложение'))
        db.session.add(Subtopics(topic_id=i, name='Вычитание'))
        db.session.add(Subtopics(topic_id=i, name='Умножение'))
        db.session.add(Subtopics(topic_id=i, name='Деление'))
        db.session.add(Subtopics(topic_id=i, name='Степени'))
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        AddContent(app)