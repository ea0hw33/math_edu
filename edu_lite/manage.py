import re
import os
import random
from edu_lite import db
from edu_lite import models

def generate_expression(subtopic_id):
    if subtopic_id == '1':
        question: str
        answer: str
        a = random.randint(0,1000)
        b = random.randint(0,1000)
        c = random.randint(0,1)
        if c:
            question = f'{a} + {b}'
            answer = str(a + b)
        else:
            question = f'{a} - {b}'
            answer = str(a - b)

        return question,answer
    elif subtopic_id== '2':
        a = round(100/random.random(),1)
        b = round(100/random.random(),1)
        c = random.randint(0,1)
        if c:
            question = f'{a} + {b}'
            answer = str(a + b)
        else:
            question = f'{a} - {b}'
            answer = str(a - b)
        return question, answer
    return '0','0'

def add_questions(subtopic_id):
    question, answer = generate_expression(subtopic_id)
    db.session.add(models.Questions(value=question, subtopic_id=subtopic_id, answer=answer))
    db.session.commit()