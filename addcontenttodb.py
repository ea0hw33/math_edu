from edu_lite import db, app
from edu_lite.models import *
from edu_lite.views import topic


def AddContent(app):
    db.session.add(Topics(name='Натуральные числа'))
    db.session.add(Topics(name='Целые числа'))
    db.session.add(Topics(name='Десятичные числа'))
    db.session.add(Topics(name='Смешанные дроби'))
    for i in range(1,4):
        db.session.add(Subtopics(topic_id=i, name='Сложение'))
        db.session.add(Subtopics(topic_id=i, name='Вычитание'))
        db.session.add(Subtopics(topic_id=i, name='Умножение'))
        db.session.add(Subtopics(topic_id=i, name='Деление'))
        db.session.add(Subtopics(topic_id=i, name='Степени'))
    db.session.add(Subtopics(topic_id=4, name='Cокращение'))
    db.session.add(Subtopics(topic_id=4, name='из смешанной в неправильную'))
    db.session.add(Subtopics(topic_id=4, name='из неправильной в смешанную'))
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        AddContent(app)