from edu_lite import db, app
from edu_lite.models import *
from passlib.hash import sha256_crypt

# new_topics = []
# new_subtopics = []
# new_questions = []

def AddContent(app):
    while True:
        f = input("Добавить новую тему?(y/n)")
        if f == 'y':
            topic = input("Введите название новой темы")
            db.session.add(Topics(name=topic))
            db.session.commit()
        else:
            topics = [t for t in Topics.query.all()]
            print("Выберите тему:")
            for i,j in zip(topics,range(len(topics))):
                print(f"{j})",i.name)
            chosen_topic = int(input())
            f = input("Создать новую подтему?(y/n)")
            if f == 'y':
                subtopic = input("Введите название новой подтемы")
                db.session.add(Subtopics(topic_id=topics[chosen_topic].id,name=subtopic))
                db.session.commit()
            else:
                subtopics = [t for t in Subtopics.query.filter_by(topic_id=topics[chosen_topic].id).all()]
                print("Выберите подтему:")
                for i, j in zip(subtopics, range(len(subtopics))):
                    print(f"{j})", i.name)
                chosen_subtopic = int(input())
                f = input("Создать новое упражнение?(y/n)")
                if f == 'y':
                    question = input("Введите текст вопроса:")
                    answer = float(input("Введите ответ для вопроса:"))
                    db.session.add(Questions(value=question,subtopic_id=subtopics[chosen_subtopic].id,answer=answer))
                    db.session.commit()
                else:
                    f = input("Хотите продолжить?(y/n)")
                    if f != "y":
                        break



if __name__=="__main__":
    with app.app_context():
        AddContent(app)