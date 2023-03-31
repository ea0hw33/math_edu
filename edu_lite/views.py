import re
import os
from datetime import datetime, timedelta, date
from passlib.hash import sha256_crypt

from flask import render_template, flash, request, redirect, session, jsonify
from edu_lite import app, db
from .forms import LoginForm, RegistrationForm, TopicForm, AttemptForm, PastAttemptsForm
from .models import Topics, Students, Questions, Attempts, Results, Subtopics
from flask_login import login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from .manage import add_questions


@app.route('/_parse_data', methods=['GET'])
def parse_data():
    if request.method == "GET":

        # only need the id we grabbed in my case.
        id = request.args.keys()
        print(id)

        # When returning data it has to be jsonify'ed and a list of tuples (id, value) to populate select fields.
        # Example: [('1', 'One'), ('2', 'Two'), ('3', 'Three')]

    # return jsonify(new_list)

@app.route('/topic', methods=['GET', 'POST'])
@login_required
def topic():
    """topic view."""

    topics = [(t.id,t.name) for t in Topics.query.all()]
    subtopics = [(st.id,st.name) for st in Subtopics.query.all()]
    form = TopicForm()
    form.topic.choices = topics
    form.subtopic.choices = subtopics
    if request.method == "POST":
        session['topic_id'] = form.topic.data
        session['subtopic_id'] = form.subtopic.data
        session['time'] = int(form.time.data)
        session['num_of_questions'] = int(form.num_of_questions.data)
        session['starttime'] = datetime.now()
        num_of_questions = session['num_of_questions']
        for _ in range(num_of_questions):
            add_questions(session['subtopic_id'])
        attempt = Attempts(student_id=session['_user_id'],
                           starttime=session['starttime'],
                           topic_id=session['topic_id'],
                           subtopic_id= session['subtopic_id'])
        db.session.add(attempt)
        db.session.commit()
        return redirect('/topic/attempt')
    return render_template('topic.html',
                           title='Тесты',
                           form=form)




@app.route('/topic/attempt', methods=['GET', 'POST'])
@login_required
def attempt():
    """Attempt view."""

    form = AttemptForm()
    questions = [(q.id,q.value) for q in Questions.query.filter_by(subtopic_id=session['subtopic_id']).all()][-session['num_of_questions']:]
    if request.method == "POST":
        attempt = Attempts.query.order_by(Attempts.starttime.desc()).filter_by(student_id=session['_user_id'],
                                            topic_id=session['topic_id'],
                                           subtopic_id=session['subtopic_id']).first()
        session['attempt_id'] = attempt.id
        for question,field in zip(questions,request.values.dicts[1].getlist('field_answer')):
                results = Results(attempt_id=attempt.id,
                                  question_id=question[0],
                                  fact_answer=str(field))
                db.session.add(results)
        endtime = datetime.now()
        attempt.endtime = endtime
        db.session.commit()
        return redirect('/topic/results')
    return render_template('attempt.html',
                            title='Тестирование',
                            form=form,
                            questions=questions)



@app.route('/topic/results')
@login_required
def results():
    """Results view."""

    results_list = []
    count = 0
    total = 0
    for result in Results.query.filter_by(attempt_id=session['attempt_id']):
        count+=1
        question = Questions.query.filter_by(id=result.id).all()[0]
        fact_ids = Results.query.filter_by(attempt_id=session['attempt_id'],
                                                               question_id=result.question_id).all()[0]

        if question.answer == fact_ids.fact_answer:
            total += 1
        results_list.append([question.value, question.answer, fact_ids.fact_answer])
    total_result = str(total) + '/' + str(count)
    return render_template('results.html',
                            title='Результаты',
                            total_result=total_result,
                            results=results_list)


@app.route('/past_attempts')
@login_required
def past_attempts():
    """Past attempts view."""

    form = PastAttemptsForm()
    form.student.choices = [(s.id, f"{s.name} {s.second_name} {s.surname}") for s in db.session.query(Students).filter(Students.isadmin == 0)]
    return render_template('past_attempts.html',
                            title='Прошлые попытки',
                            form=form)



@app.route('/get_past_attempts', methods=['POST'])
@login_required
def get_past_attempts():
    """Util view for AJAX load of past attempts."""

    # topic_id = request.form['topic']
    student_id = request.form['student']
    topic_date = request.form['date']
    attempts_dict = {}
    topic_day = datetime.strptime(topic_date, '%Y-%m-%d')
    next_day = topic_day + timedelta(days=1)
    attempts = [(a.id, a.starttime, a.endtime) for a in db.session.query(Attempts).filter(Attempts.student_id==student_id)]
    for attempt in attempts:
        attempts_dict[str(attempt[0])] = {'start': attempt[1], 'end': attempt[2]}
    print(attempts_dict)
    return jsonify(attempts_dict)


@app.route('/logout')
@login_required
def logout():
    """Logout view."""

    logout_user()
    return redirect('/login')


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login view."""

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        form_login = form.login.data
        form_password = form.password.data
        form_remember = form.remember_me.data
        user = form.validate_user(form_login, form_password)
        if user:
                login_user(user, remember = form_remember)
                student = Students.query.get(session['_user_id'])
                if student.isadmin == 1:
                    return redirect('/admin')
                else:
                    return redirect('/topic')
    return render_template('login.html',
                           title='Вход',
                           form=form)




@app.route('/registration', methods=['GET', 'POST'])
@login_required
def registration():
    """Registration view."""

    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        form_name = form.name.data
        form_sec_name = form.second_name.data
        form_surname = form.surname.data
        form_login = form.login.data
        form_password = form.password.data
        form_password_repeat = form.password_repeat.data
        if form_password == form_password_repeat:
            form.register_user(str(form_name), str(form_sec_name), str(form_surname), str(form_login),
                                   form_password)
            return 'User {} was added'.format(form_name)
    return render_template('registration.html',
                           title='Registration',
                           form=form)




@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    """Admin view."""

    student = Students.query.get(session['_user_id'])
    if student.isadmin != 1:
        return "Access denied!!!"
    else:
        form_reg = RegistrationForm()
        past_attempt = PastAttemptsForm()
        past_attempt.student.choices = [(s.id, f"{s.name} {s.second_name} {s.surname}") for s in db.session.query(Students).filter(Students.isadmin==0)]

        if request.method == 'POST' and past_attempt.validate_on_submit():
            return render_template('past_attempts.html',title='Прошлые попытки')


        if request.method == 'POST' and form_reg.validate_on_submit():

            form_name = form_reg.name.data
            form_sec_name = form_reg.second_name.data
            form_surname = form_reg.surname.data
            form_login = form_reg.login.data
            form_password = form_reg.password.data
            form_password_repeat = form_reg.password_repeat.data
            if form_password == form_password_repeat:
                form_reg.register_user(str(form_name),str(form_sec_name),str(form_surname),str(form_login), form_password)
                message = 'Пользователь {} добавлен'.format(form_name)
                return render_template('admin.html',
                                       title='Админка',
                                       message=message,
                                       form_reg=form_reg,
                                       past_attempt=past_attempt)
        return render_template('admin.html',
                               title='Админка',
                               form_reg=form_reg,
                               past_attempt=past_attempt)
        