import re
import os
from datetime import datetime, timedelta, date
from passlib.hash import sha256_crypt

from flask import render_template, flash, request, redirect, session, jsonify
from edu_lite import app, db
from .forms import LoginForm, RegistrationForm, TopicForm, AttemptForm, FileForm, NewTopicForm, PastAttemptsForm
from .models import Topics, Students, Questions, Answers, Attempts, Results
from flask_login import login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from .manage import add_questions



@app.route('/topic', methods=['GET', 'POST'])
@login_required
def topic():
    """topic view."""

    topics = [(t.id,t.name) for t in Topics.query.all()]
    form = TopicForm()
    form.topic.choices = topics
    # form.url_topic.append()
    # for i,j in zip(form.url_topic,topics):
    #     i.label = j
    # for i in topics:
    #     form.topic.label = i

    if request.method == "POST":
        session['topic_id'] = form.topic.data
        session['starttime'] = datetime.now()
        attempt = Attempts(student_id=session['_user_id'],
                           starttime=session['starttime'],
                           topic_id=session['topic_id'])
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
    questions = [(q.id,q.value,q.type) for q in Questions.query.filter_by(topic_id=session['topic_id']).all()]
    print(questions)
    if request.method == "POST":
        attempt = Attempts.query.order_by(Attempts.starttime.desc()).filter_by(student_id=session['_user_id'],
                                           topic_id=session['topic_id']).first()
        session['attempt_id'] = attempt.id
        for question in questions:
            if question[2] == 0:   # Check on single answer
                form_answer = request.form.get(str(question[0]))
                results = Results(attempt_id=attempt.id,
                                  question_id=question[0],
                                  fact_id=int(form_answer))
                db.session.add(results)
            elif question[2] == 1:
                form_answers = request.form.getlist(str(question[0]))
                int_form_answers =  [int(x) for x in form_answers]
                for answer in int_form_answers:
                    results = Results(attempt_id=attempt.id,
                                      question_id=question[0],
                                      fact_id=answer)
                    db.session.add(results)
            else:
                form_answer = request.form.get(str(question[0]))
                results = Results(attempt_id=attempt.id,
                                  question_id=question[0],
                                  fact_id=int(form_answer))
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
    questions = [(q.id,q.value,q.type) for q in Questions.query.filter_by(topic_id=session['topic_id']).all()]
    # Count of total result in format 'count of correct answers/count of all answers'
    total = 0
    for question in questions:
        fact_ids = [r.fact_id for r in Results.query.filter_by(attempt_id=session['attempt_id'], 
                                                               question_id=question[0]).all()]
        if question[2] == 0:
            correct_answer = Answers.query.filter_by(question_id=question[0], iscorrect=1).first()
            if correct_answer.id in fact_ids:
                total += 1
        if question[2] == 1:
            wrong = 0
            correct_answers = Answers.query.filter_by(question_id=question[0], iscorrect=1).all()
            for answer in correct_answers:
                if answer.id not in fact_ids:
                    wrong += 1
                for fact_id in fact_ids:
                    fact = Answers.query.get(fact_id)
                    if fact.iscorrect == 0:
                        wrong += 1
            if wrong == 0:
                total += 1
        answers = Answers.query.filter_by(question_id=question[0]).all()
        results_list.append([question[1], answers, fact_ids])
    count = 0
    for question in questions:
        count += 1
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

    topic_id = request.form['topic']
    student_id = request.form['student']
    topic_date = request.form['date']
    attempts_dict = {}
    topic_day = datetime.strptime(topic_date, '%Y-%m-%d')
    next_day = topic_day + timedelta(days=1)
    #attempts = [(a.id, a.starttime, a.endtime) for a in Attempts.filter(Attempts.topic_id==topic_id,
    #                                                                    Attempts.student_id==student_id,
    #                                                                    Attempts.starttime>=topic_day,
    #                                                                    Attempts.endtime <= next_day).all()]
    attempts = [(a.id, a.starttime, a.endtime) for a in db.session.query(Attempts).filter(Attempts.topic_id==topic_id,
                                                                                   Attempts.student_id==student_id,
                                                                                   Attempts.starttime>=topic_day,
                                                                                   Attempts.endtime <= next_day).all()]
    for attempt in attempts:
        attempts_dict[str(attempt[0])] = {'start': attempt[1], 'end': attempt[2]}
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
    # print(form.validate_on_submit(),form.is_submitted(),'_')
    if request.method == "POST" and form.validate_on_submit():
        form_name = form.name.data
        form_password = form.password.data
        form_remember = form.remember_me.data
        user = form.validate_user(form_name, form_password)
        # print(user,'_')
        if user:
                login_user(user, remember = form_remember)
                # print(session)
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
        form_file = FileForm()
        names = [(t.id,t.name) for t in Topics.query.all()]
        form_file.topic.choices = names
        form_new_topic = NewTopicForm()
        form_reg = RegistrationForm()
        if request.method == 'POST' and form_file.file.data:
            filename = secure_filename(form_file.file.data.filename)
            form_file.file.data.save('uploads/' + filename)
            topic_id = form_file.topic.data
            add_questions(topic_id,filename)
            message = 'Вопросы из файла {} добавлены'.format(filename) 
            return render_template('admin.html',
                                   title='Админка',
                                   message=message,
                                   form_new_topic=form_new_topic,
                                   form_reg=form_reg,
                                   form_file=form_file)
        if request.method == 'POST' and form_new_topic.validate_on_submit():
            topic_name = request.form.get('topic_name')
            new_topic = Topics(name=topic_name)
            db.session.add(new_topic)
            db.session.commit()
            message = 'Добавлен тест {}'.format(form_new_topic.topic_name.data)
            return render_template('admin.html',
                                   title='Админка',
                                   message=message,
                                   form_new_topic=form_new_topic,
                                   form_reg=form_reg,
                                   form_file=form_file)
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
                                       form_new_topic=form_new_topic,
                                       form_reg=form_reg,
                                       form_file=form_file)
        return render_template('admin.html',
                               title='Админка',
                               form_new_topic=form_new_topic,
                               form_reg=form_reg,
                               form_file=form_file)
        