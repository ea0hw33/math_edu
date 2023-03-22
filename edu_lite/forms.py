import re
from flask_wtf import FlaskForm, Form
from wtforms import BooleanField, StringField, PasswordField, FileField, SelectField, RadioField, SelectMultipleField, widgets
from wtforms.fields import DateField
from wtforms.validators import Email, DataRequired, EqualTo, ValidationError, InputRequired
from edu_lite import db
from .models import Students, Questions, Topics, Attempts
from passlib.hash import sha256_crypt


def exists_user(form, field):
    """
    Username validator.
    
    Checks if user exists in base with name.
    """

    user = Students.query.filter_by(name=field.data).first()
    if not user:
        raise ValidationError('There is no user with name {}'.format(field.data))


def validate_username(form, field):
    """
    Username already in use validator.

    Count the number of user ids for that username
    if it's not 0, there's a user with that username already.
    """

    if db.session.query(db.func.count(Students.id)).filter_by(name=field.data).scalar():
        raise ValidationError('Name already in use')



class TopicForm(FlaskForm):
    """Test form."""

    topic = SelectField('Темы', choices=[])
    subtopic = SelectField('Подтемы', choices=[])




class LoginForm(FlaskForm):
    """Login form."""

    name = StringField('Имя', validators=[DataRequired(), exists_user])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня", default=False)

    def validate_user(self, form_name, form_password):
        """User authorization check."""

        user = Students.query.filter_by(name=form_name).first()
        if user:
            base_password = user.password
            if sha256_crypt.verify(form_password, base_password) == True:
                return user
            else:
                raise ValidationError('Wrong password')


class RegistrationForm(LoginForm):
    """Registration form."""

    name = StringField('Имя', validators=[DataRequired(), validate_username])
    password_repeat = PasswordField('Повтор пароля', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

    def register_user(self, form_name, form_password):
        """User registration."""

        crypt_password = sha256_crypt.hash(form_password)
        new_user = Students(form_name, crypt_password, 0)  
        db.session.add(new_user)
        db.session.commit()

class AttemptForm(FlaskForm):
    """Form for pass atempt."""

    # answer = RadioField('answer', choices=[], validators=[])
    # multi_answer = MultiCheckboxField('multi_answer', choices=[], validators=[])
    field_answer = StringField('field_answer', validators = [DataRequired()])
    def add_field(self, question_id):
        # answers = [(a.id, a.value) for a in Answers.query.filter_by(question_id=question_id).all()]
        self.field_answer.id = question_id
        # self.field_answer.validators = answers
        self.field_answer.name= str(question_id)
        # return field_answer

class PastAttemptsForm(TopicForm):
    """Past attempts form."""

    student = SelectField('Студент', choices=[])
    date = DateField('Дата', format="%Y-%m-%d")



# class FileForm(TopicForm):
#     """File form."""
#
#     file = FileField('Файл', validators=[DataRequired()])

# class NewTopicForm(FlaskForm):
#     """New test form."""
#
#     topic_name = StringField('Название теста', validators=[DataRequired()])

