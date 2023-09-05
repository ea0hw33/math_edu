import re
import os
from random import *
from edu_lite import db
from edu_lite import models


class Manage():
    

    @staticmethod
    def generate_expression(topicId, subtopicId):
        # print(topicId,subtopicId)
        match topicId:
            case '1,2,3,4,5':
                return Manage.integers(subtopicId)
            case '6,7,8,9,10':
                return Manage.wholeNumbers(subtopicId)
            case '11,12,13,14,15':
                return Manage.decimalNumbers(subtopicId)
            case '16,17,18':
                return Manage.decimalNumbers(subtopicId)
            

    @staticmethod
    def integers(Subtopic):
        question = ''
        answer = ''
        match Subtopic:
            case 1:
                answer = randint(20, 100)
                a = randint(1, answer)
                b = answer - a
                question = f"{b} + {a}"

            case 2:
                answer = randint(20, 100)
                a = randint(1, answer)
                b = answer + a
                question = f"{b} - {a}"

            case 3:
                a = randint(1, 31)
                b = randint(1, 31)
                answer = a*b
                question = f"{a} * {b}"


            case 4:
                answer = randint(1, 31)
                a = randint(1, 31)
                b = answer * a
                question = f"{b} / {a}"

            case 5:
                sqr = randint(2, 4)
                a = 0
                if sqr == 2:
                    a = randint(2, 31)
                if sqr == 3:
                    a = randint(2, 9)
                if sqr == 4:
                    a = randint(2, 5)
                question = f"{a} ^ {sqr}"
                answer = a ** sqr

        return question, str(answer)
    

    @staticmethod
    def wholeNumbers(Subtopic):
        question = ''
        answer = ''
        match Subtopic:
            case 6:
                answer = randint(-99, 50)
                a = randint(-50, 0)
                mixab = randint(0, 1)
                b = answer - a
                question = (lambda x: f"{b} + {a}" if x else f"{a} + {b}")(mixab)

            case 7:
                answer = randint(-99, 50)
                a = randint(-50, 50)
                b = answer + a
                question = f"{b} - {a}"

            case 8:
                b = randint(-31, 31)
                a = randint(-31, 31)
                answer = b*a
                question = f"{b} * {a}"

            case 9:
                b = randint(-31, 31)
                a = randint(-31, 31)
                question = f"{b * a} / {a}"
                answer = b

            case 10:
                sqr = randint(2, 4)
                a = 0
                if sqr == 2:
                    a = choice([i for i in range(-31, 32) if i not in [0, 1, -1]])
                if sqr == 3:
                    a = choice([i for i in range(-9, 10) if i not in [0, 1, -1]])
                if sqr == 4:
                    a = choice([i for i in range(-5, 6) if i not in [0, 1, -1]])
                question = f"{a} ^ {sqr}"
                answer = a ** sqr

        return question, str(answer)
    

    @staticmethod
    def decimalNumbers(Subtopic):
        question = ''
        answer = ''
        match Subtopic:
            case 11:
                answer = round(random() * 300, 2)
                a = round(random() * int(answer), 2)
                mixab = randint(0, 1)
                b = round(answer - a, 2)
                answer = round(a + b, 2)
                question = (lambda x: f"{b} + {a}" if x else f"{a} + {b}")(mixab)

            case 12:
                answer = round(random() * 100, 2)
                a = round(random() * 100, 2)
                b = round(answer + a, 2)
                question = f"{b} - {a}"

            case 13:
                answer = round(random() * 10, 2)
                a = randint(1, 10)
                b = round(answer / a, 2)
                mixab = randint(0, 1)
                answer = round(b * a, 2)
                question = (lambda x: f"{b} * {a}" if x else f"{a} * {b}")(mixab)

            case 14:
                # answer = round(random() * 100, 2)
                a = randint(2, 10)
                b = round(random() * 20, 2)
                answer = round(b / a, 2)
                question = f"{b} / {a}"

            case 15:
                sqr = randint(2, 3)
                a = 0
                if sqr == 2:
                    if randint(0, 1):
                        a = float(f'0.{randint(11, 31)}')
                    else:
                        a = round(random() * 10, 1)
                if sqr == 3:
                    a = float(f'0.{randint(1, 10)}')
                question = f"{a} ^ {sqr}"
                answer = round(a ** sqr, sqr*2)
        return question, str(answer)
    
    
    @staticmethod
    def mixedFractions(Subtopic):
        
        def iseven(number):
            if number % 2 == 0:
                return True
            else:
                return False
        
        def getIrreducibleFrac():
            denominator = randint(3,11)
            numerator = randint(1,denominator-1)
            
            while any([math.gcd(denominator,numerator)>1,
                        iseven(numerator)==iseven(denominator)]):
                numerator = randint(1,denominator-1)
            
            return numerator,denominator
        
        
        question = ''
        answer = ''
        match Subtopic: 
            case 16:
                numerator, denominator = getIrreducibleFrac()
                
                a = 0
                while a in [-1,0,1]:
                    a = randint(-11,11)
                    
                question = f"{numerator*a}/{denominator*a}"
                answer = f"{numerator}/{denominator}"
            case 17:
                numerator, denominator = getIrreducibleFrac()
                wholenum = randint(2,13)
                question = f"{wholenum}({numerator}/{denominator})"
                answer = f"{wholenum*denominator+numerator}/{denominator}"
            case 18:
                numerator, denominator = getIrreducibleFrac()
                wholenum = randint(2,13)
                answer = f"{wholenum}({numerator}/{denominator})"
                question = f"{wholenum*denominator+numerator}/{denominator}"
        return question, answer

def add_questions(topicId,subtopicId):
    question, answer = Manage.generate_expression(topicId,int(subtopicId))
    db.session.add(models.Questions(value=question, subtopic_id=subtopicId, answer=answer))
    db.session.commit()
