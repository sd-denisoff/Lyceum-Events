from flask import redirect, render_template, request, session
from web import app, db, mail
from web.models import User, Event, Feedback
from web.forms import LoginForm, RegForm, CreateEventForm, FeedbackForm, ChangePasswordForm, ChangeMailForm, ForgetPasswordForm
from flask_mail import Message
from passlib.hash import pbkdf2_sha256
import random


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('main.html', all_events=Event.get_all())


@app.route('/make', methods=['GET', 'POST'])
def make():
    form = CreateEventForm()
    if form.validate_on_submit():
        event = Event(form.title.data, form.content.data, form.date.data, session['username'])
        event.save()
        return redirect('/')
    return render_template('make.html', form=form)


@app.route('/event/<int:event_id>', methods=['GET','POST'])
def event(event_id):
    action = '/event/' + str(event_id)
    if request.method == 'POST':
        event = Event.get_event(event_id)
        Event.query.filter_by(id=event_id).update(dict(members=event.members + 1))
        db.session.commit()
        return redirect('/')
    return render_template('event.html', event=Event.get_event(event_id), event_id=event_id, action=action)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_all()
        for i in user:
            check = pbkdf2_sha256.verify(request.form['password'], i.password) # Проверка введенных данных
            if request.form['login'] == i.login and check == True:
                session['logged_in'] = True # Начало сессии
                session['username'] = i.login
                return redirect('/account') # После успешного входа пользователя перенаправляет в личный кабинет
        if session['logged_in'] != True:
            return render_template('login.html', error_text='Неправильный логин или пароль.', form=form)
    return render_template('login.html', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegForm()
    if form.validate_on_submit():
        users = User.get_all()
        for i in users:     # Проверка на уникальность логина и почты
            if (form.email.data == i.email):
                return render_template('reg.html', error_text='Пользователь с такой почтой уже существует', form=form)
            if (form.login.data == i.login):
                return render_template('reg.html', error_text='Пользователь с таким логином уже существует', form=form)
        secret_pass = pbkdf2_sha256.hash(form.password.data)        # Шифровка пароля и сохранение пользователя
        user = User(form.name.data, form.email.data, form.login.data, secret_pass)
        user.save()
        session['logged_in'] = True
        session['username'] = form.login.data
        return redirect('/')
    return render_template('reg.html', form=form)


@app.route('/info', methods=['GET', 'POST'])
def info():
    return render_template('info.html')


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    all_feedbacks = Feedback.get_all()
    if form.validate_on_submit():
        review = Feedback(form.content.data, session['username'])
        review.save()
        return redirect('/feedback')
    return render_template('feedback.html', form=form, all_feedbacks=all_feedbacks)


@app.route('/account', methods=['GET', 'POST'])
def account():
    name = User.get_name(session['username'])
    login = session['username']
    all_events = Event.get_user_events(login)
    return render_template('account.html', name=name, login=login, all_events=all_events)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False # Заканчивает сессию
    return redirect('/')


@app.route('/changepass', methods=['GET', 'POST'])
def change():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Проверка на то, что ввели настоящий старый пароль
        old_pass = form.old_password.data
        real_old_pass = User.get_password(session['username'])
        check = pbkdf2_sha256.verify(request.form['old_password'], real_old_pass)
        if check != True:
            return render_template('change_pass.html', error_text='Вы ввели неправильный старый пароль.', form=form)

        new_pass = form.new_password.data
        confirm_new_pass = form.confirm_new_password.data
        # Проверка на то, что новый пароль не совпадает со старым.
        if request.form['old_password'] == request.form['new_password']:
            return render_template('change_pass.html', error_text='Новый пароль не может совпадать со старым.', form=form)
        new_secret = pbkdf2_sha256.hash(new_pass)
        # Сохранение новых данных
        User.query.filter_by(login=session['username']).update(dict(password=new_secret))
        db.session.commit()
        return redirect('/account')
    return render_template('change_pass.html', form=form)


@app.route('/changemail', methods=['GET', 'POST'])
def changemail():
    form = ChangeMailForm()
    if form.validate_on_submit():
        #  Проверка на правильность пароля и старой почты
        real_password = User.get_password(session['username'])
        check = pbkdf2_sha256.verify(request.form['password'], real_password)
        if check != True:
            return render_template('change_email.html', error_text = 'Вы ввели неправильный пароль.', form=form)
        if form.old_email.data != User.get_email(session['username']):
            return render_template('change_email.html', error_text = 'Вы ввели неправильный старый email.', form=form)

        # Проверка на уникальность новой почты
        users = User.get_all()
        for i in users:
            if (form.new_email.data == i.email):
                return render_template('change_email.html', error_text = 'Пользователь с такой почтой уже существует.', form=form)
        # Сохранение новых данных
        User.query.filter_by(login=session['username']).update(dict(email=form.new_email.data))
        db.session.commit()
        return redirect('/account')
    return render_template('change_email.html', form=form)


@app.route('/forget', methods=['GET', 'POST'])
def forget():
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        users = User.get_all()
        check = False
        for i in users:
            if (form.email.data == i.email):
                check = True
                user_mail = form.email.data
                random_pass = (''.join([random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) for x in range(8)]))
                msg = Message('Восстановление пароля', sender="alexkoritsa@yandex.ru", recipients=[user_mail])
                msg.html = render_template('mail.html', password=random_pass, login=i.login, name=i.name)
                mail.send(msg)

                secret_pass = pbkdf2_sha256.hash(random_pass)
                User.query.filter_by(login=i.login).update(dict(password=secret_pass))
                db.session.commit()
        if check != True:
            return render_template('forget.html', error_text='Пользователя с таким email не существует.', form=form)
        return redirect('/')
    return render_template('forget.html', form=form)


# Страница 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
