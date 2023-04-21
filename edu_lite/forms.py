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
    
    Checks if user exists in base with login.
    """

    user = Students.query.filter_by(login=field.data).first()
    if not user:
        raise ValidationError('There is no user with name {}'.format(field.data))


def validate_username(form, field):
    """
    Login already in use validator.

    Count the number of user ids for that username
    if it's not 0, there's a user with that username already.
    """

    if db.session.query(db.func.count(Students.id)).filter_by(login=field.data).scalar():
        raise ValidationError('Name already in use')



class TopicForm(FlaskForm):
    """Test form."""

    topic = SelectField('Темы', choices=[])
    subtopic = SelectField('Подтемы', choices=[])
    num_of_questions = StringField('Количество вопросов', validators=[DataRequired()])
    time = StringField('Время прохождения теста', validators=[DataRequired()])




class LoginForm(FlaskForm):
    """Login form."""

    login = StringField('Логин', validators=[DataRequired(), exists_user])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня", default=False)

    def validate_user(self, form_login, form_password):
        """User authorization check."""

        user = Students.query.filter_by(login=form_login).first()
        if user:
            base_password = user.password
            if sha256_crypt.verify(form_password, base_password) == True:
                return user
            else:
                return None


class RegistrationForm(LoginForm):
    """Registration form."""

    name = StringField('Имя', validators=[DataRequired()])
    second_name = StringField('Фамилия', validators=[DataRequired()])
    surname = StringField('Отчество', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired(), validate_username])
    password_repeat = PasswordField('Повтор пароля', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

    def register_user(self, form_name, form_sec_name, form_surname, form_login, form_password):
        """User registration."""

        crypt_password = sha256_crypt.hash(form_password)
        new_user = Students(form_name, form_sec_name, form_surname, form_login, crypt_password, 0)
        db.session.add(new_user)
        db.session.commit()

class AttemptForm(FlaskForm):
    """Form for pass atempt."""

    field_answer = StringField('field_answer')
    def add_field(self, question_id):
        self.field_answer.id = question_id
        self.field_answer.name= str(question_id)

class PastAttemptsForm(TopicForm):
    """Past attempts form."""

    student = SelectField('Студент', choices=[])
    date = DateField('Дата', format="%Y-%m-%d")