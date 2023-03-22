from edu_lite import db


class Topics(db.Model):
    """Topics model."""

    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class Subtopics(db.Model):
    """Subtopic model"""
    __tablename__ = 'subtopics'


    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))
    name = db.Column(db.String)

class Questions(db.Model):
    """Questions model."""

    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String)
    subtopic_id = db.Column(db.Integer, db.ForeignKey("subtopics.id"))
    answer = db.Column(db.Float)





# class Answers(db.Model):
#     """Answers model."""
#
#     __tablename__ = 'answers'
#
#     id = db.Column(db.Integer, primary_key=True)
#     value = db.Column(db.String)
#     question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
#     iscorrect = db.Column(db.Integer)



class Attempts(db.Model):
    """Attempts model."""

    __tablename__ = 'attempts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    starttime = db.Column(db.DateTime)
    endtime = db.Column(db.DateTime)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))
    subtopic_id = db.Column(db.Integer, db.ForeignKey("subtopics.id"))



class Results(db.Model):
    """Results model."""

    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("attempts.id"))
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    fact_id = db.Column(db.Float)



class Students(db.Model):
    """Users(students) model."""

    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    password = db.Column(db.String)
    isadmin = db.Column(db.Integer)


    def __init__(self, name, password, isadmin):
        self.name = name
        self.password = password
        self.isadmin = isadmin
        

    # These methods go with flask_login  
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)




