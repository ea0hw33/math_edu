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
    # form.subtopic.choices = [(st.id,st.name) for st in Subtopics.query.filter_by(topic_id=session['topic_id']).all()]
    # form.url_topic.append()
    # for i,j in zip(form.url_topic,topics):
    #     i.label = j
    # for i in topics:
    #     form.topic.label = i
    if request.method == "POST":
        session['topic_id'] = form.topic.data
        session['subtopic_id'] = form.subtopic.data
        session['starttime'] = datetime.now()
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
    questions = [(q.id,q.value) for q in Questions.query.filter_by(subtopic_id=session['subtopic_id']).all()]
    if request.method == "POST":
        attempt = Attempts.query.order_by(Attempts.starttime.desc()).filter_by(student_id=session['_user_id'],
                                            topic_id=session['topic_id'],
                                           subtopic_id=session['subtopic_id']).first()
        session['attempt_id'] = attempt.id
        for question,field in zip(questions,request.values.dicts[1].getlist('field_answer')):
                results = Results(attempt_id=attempt.id,
                                  question_id=question[0],
                                  fact_id=float(field))
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
    questions = [(q.id,q.value,q.answer) for q in Questions.query.filter_by(subtopic_id=session['subtopic_id']).all()]
    # Count of total result in format 'count of correct answers/count of all answers'
    total = 0
    for question in questions:
        fact_ids = [r.fact_id for r in Results.query.filter_by(attempt_id=session['attempt_id'], 
                                                               question_id=question[0]).all()]

        if question[2] in fact_ids:
            total += 1
        # answers = Answers.query.filter_by(question_id=question[0]).all()
        # print(questions)
        results_list.append([question[1], question[2], *fact_ids])
    count = 0
    count = len(questions)
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
    topics = [(t.id,t.name) for t in Topics.query.all()]
    form.topics.choices = topics
    students = [(s.id,s.name) for s in Students.query.all()]
    form.student.choices = students
    return render_template('past_attempts.html',
                            title='Прошлые попытки',
                            form=form)



@app.route('/get_past_attempts', methods=['POST'])
@login_required
def get_past_attempts():
    """Util view for AJAX load of past attempts."""

    # topic_id = request.form['topic']
    student_id = request.form['student']
    # topic_date = request.form['date']
    attempts_dict = {}
    # topic_day = datetime.strptime(topic_date, '%Y-%m-%d')
    # next_day = topic_day + timedelta(days=1)
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
        form_name = form.name.data
        form_password = form.password.data
        form_remember = form.remember_me.data
        user = form.validate_user(form_name, form_password)
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
        form_password = form.password.data
        form_password_repeat = form.password_repeat.data
        if form_password == form_password_repeat:
            form.register_user(form_name, form_password)
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
        if request.method == 'POST' and form_reg.validate_on_submit():
            form_name = form_reg.name.data
            form_password = form_reg.password.data
            form_password_repeat = form_reg.password_repeat.data
            if form_password == form_password_repeat:
                form_reg.register_user(str(form_name), form_password)
                message = 'Пользователь {} добавлен'.format(form_name)
                return render_template('admin.html',
                                       title='Админка',
                                       message=message,
                                       form_reg=form_reg)
        return render_template('admin.html',
                               title='Админка',
                               form_reg=form_reg)
        