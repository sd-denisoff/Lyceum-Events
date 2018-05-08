from flask import redirect, render_template, request, session
from web import app, db, mail
from web.models import User, Event, Feedback
from web.forms import LoginForm, RegForm, CreateEventForm, FeedbackForm, ChangePasswordForm, ChangeMailForm, ForgetPasswordForm, BanUserForm, AmnestyUserForm, AddAdminForm, RemoveAdminForm
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
    if request.method == 'POST':
        id = int(request.form['option'])
        Option.query.filter_by(id=id).update(dict(votes=Option.get_votes(vote_id, id) + 1))
        db.session.commit()
        return render_template('voting.html', voting=Voting.get_voting(vote_id), options=Option.get_options(vote_id), mode=Voting.get_mode(vote_id), vote_id=vote_id, isResult=1)
    return render_template('event.html', event=Event.get_event(event_id), event_id=event_id, is_voted=1)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_all()
        banned = False
        for i in user:
            check = pbkdf2_sha256.verify(request.form['password'], i.password) # Проверка введенных данных
            if i.role == 'ban':
                banned = True
            if request.form['login'] == i.login and check == True and i.role != 'ban':
                session['logged_in'] = True # Начало сессии
                session['username'] = i.login
                return redirect('/account') # После успешного входа пользователя перенаправляет в личный кабинет
        if banned == True:
            return render_template('login.html', error_text='Вы забанены администратором. По всем вопросам Вы можете написать на почту alexkoritsa@yandex.ru.', form=form)
        if session['logged_in'] != True and banned != True:
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
        if form.login.data == 'admin':
            user_role = 'admin'
        else:
            user_role = 'user'
        secret_pass = pbkdf2_sha256.hash(form.password.data)        # Шифровка пароля и сохранение пользователя
        user = User(form.name.data, form.email.data, form.login.data, secret_pass, user_role)
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
    role = User.get_role(session['username'])
    all_votings = Voting.get_user_votings(login)
    return render_template('account.html', name=name, login=login, role=role, all_votings=all_votings)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False # Заканчивает сессию
    return redirect('/')

@app.route('/changepass', methods=['GET', 'POST'])
def change():
    form = ChangePass()
    if form.validate_on_submit():
        # Проверка на то, что ввели настоящий старый пароль
        old_pass = form.old_pass.data
        real_old_pass = User.get_password(session['username'])
        check = pbkdf2_sha256.verify(request.form['old_pass'], real_old_pass)
        if check != True:
            return render_template('change_pass.html', error_text='Вы ввели неправильный старый пароль.', form=form)

        new_pass = form.new_pass.data
        confirm_new_pass = form.confirm_new_pass.data
        # Проверка на то, что новый пароль не совпадает со старым.
        if request.form['old_pass'] == request.form['new_pass']:
            return render_template('change_pass.html', error_text='Новый пароль не может совпадать со старым.', form=form)
        new_secret = pbkdf2_sha256.hash(new_pass)
        # Сохранение новых данных
        User.query.filter_by(login=session['username']).update(dict(password=new_secret))
        db.session.commit()
        return redirect('/account')
    return render_template('change_pass.html', form=form)

@app.route('/changemail', methods=['GET', 'POST'])
def changemail():
    form = ChangeMail()
    if form.validate_on_submit():
        #  Проверка на правильность пароля и старой почты
        real_password = User.get_password(session['username'])
        check = pbkdf2_sha256.verify(request.form['password'], real_password)
        if check != True:
            return render_template('/change_email.html', error_text = 'Вы ввели неправильный пароль.', form=form)
        if form.old_mail.data != User.get_email(session['username']):
            return render_template('/change_email.html', error_text = 'Вы ввели неправильный старый email.', form=form)

        # Проверка на уникальность новой почты
        users = User.get_all()
        for i in users:
            if (form.new_mail.data == i.email):
                return render_template('change_email.html', error_text = 'Пользователь с такой почтой уже существует.', form = form)
        # Сохранение новых данных
        User.query.filter_by(login=session['username']).update(dict(email=form.new_mail.data))
        db.session.commit()
        return redirect('/account')
    return render_template('change_email.html', form=form)

@app.route('/forget', methods=['GET', 'POST'])
def forget():
    form = Forget()
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
    return render_template('forget.html', form=form)

@app.route('/admintable', methods=['GET', 'POST'])
def admintable():
    form = BanUser()
    form2 = AmnestyUser()
    all_users = User.get_all()
    role = User.get_role(session['username'])
    check = False
    check2 = False

    # Форма помилования
    if form2.validate_on_submit():
        if form2.unban.data == session['username']:
            return render_template('admintable.html', role = role, all_users = all_users, error_text2 = 'Помиловать самого себя? Самолюбиво, но нет.', form = form, form2 = form2)

        for i in all_users:
            if (form2.unban.data == i.login):
                check2 = True
                if i.role == 'user':
                    return render_template('admintable.html', role = role, all_users = all_users, error_text2 = 'Этот пользователь не забанен.', form = form, form2 = form2)
                User.query.filter_by(login=i.login).update(dict(role='user'))
                db.session.commit()
                return render_template('admintable.html', role = role, all_users = all_users, form = form, form2 = form2, success_text2 = 'Пользователь помилован! Слава администратору!')

        if check2 != True:
            return render_template('admintable.html', role = role, all_users = all_users, error_text2 = 'Пользователя с таким логином не существует.', form = form, form2 = form2)

    # Форма бана
    if form.validate_on_submit():
        if form.login.data == session['username']:
            return render_template('admintable.html', role = role, all_users = all_users, error_text = 'Самого себя забанить? Вы сумасшедший.', form = form, form2 = form2)

        for i in all_users:
            if(form.login.data == i.login):
                check = True
                if i.role == 'ban':
                    return render_template('admintable.html', role=role, all_users = all_users, error_text='Этот пользователь уже забанен.', form = form, form2 = form2)
                if i.role == 'admin':
                    return render_template('admintable.html', role = role, all_users = all_users, error_text = 'Админа нельзя забанить.', form = form, form2 = form2)
                User.query.filter_by(login=i.login).update(dict(role='ban'))
                db.session.commit()
                return render_template('admintable.html', role = role, all_users = all_users, form = form, form2 = form2, success_text = 'Пользователь успешно забанен.')
        if check != True:
            return render_template('admintable.html', role = role, all_users = all_users, error_text = 'Пользователя с таким логином не существует', form = form, form2 = form2)

    return render_template('admintable.html', all_users = all_users, form = form, role = role, form2 = form2)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    all_users = User.get_all()
    role = User.get_role(session['username'])
    form1 = AddModerator(prefix="form1")
    form2 = RemoveModerator(prefix="form2")
    check1 = False
    check2 = False
    if form2.validate_on_submit() and form2.password.data and form2.password.data:
        if form2.login.data == session['username']:
            return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text2 = 'Так нельзя. Вы администратор.')
        user_password = User.get_password(session['username'])
        check_pass = pbkdf2_sha256.verify(form2.password.data, user_password)
        if check_pass != True:
            return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text2 = 'Вы ввели неправильный пароль.')

        for i in all_users:
            if form2.login.data == i.login:
                check2 = True
                if i.role == 'user' or i.role == 'ban':
                    return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text2 = 'У этого пользователя нет прав модератора.')
                if i.role == 'admin':
                    return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text2 = 'Вы не можете лишить прав другого администратора.')
                User.query.filter_by(login=i.login).update(dict(role='user'))
                db.session.commit()
                return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2, success_text2 = 'Этот пользователь теперь не модератор.')

    if form1.validate_on_submit():
        if form1.login.data == session['username']:
            return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text1 = 'Зачем? У вас уже есть права администратора.')

        user_password = User.get_password(session['username'])
        check = pbkdf2_sha256.verify(form1.password.data, user_password)
        if check != True:
            return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text1 = 'Вы ввели неправильный пароль.')

        for i in all_users:
            if form1.login.data == i.login:
                check1 = True
                if i.role == 'ban':
                    return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text1 = 'Этот пользователь забанен.')
                #if i.role == 'moderator':
                #    return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text1 = 'Этот пользователь уже модератор.')
                if i.role == 'admin':
                    return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text1 = 'Этот пользователь является администратором.')
                User.query.filter_by(login=i.login).update(dict(role='moderator'))
                db.session.commit()
                return render_template('admin.html', role = role, all_users = all_users, form1 = form1, form2 = form2, success_text1 = 'Пользователь успешно добавлен в модераторы.')
        if check1 != True:
            return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text1 = 'Пользователя с таким логином не существует.')
    return render_template('admin.html', all_users = all_users, role = role, form1 = form1, form2 = form2)

@app.route('/king', methods=['GET', 'POST'])
def king():
    all_users = User.get_all()
    role = User.get_role(session['username'])
    form1 = AddAdmin(prefix="form1")
    form2 = RemoveAdmin(prefix="form2")
    check1 = False
    check2 = False

    if form1.validate_on_submit():
        if form1.login.data == session['username']:
            return render_template('king.html', all_users = all_users, role = role, form1 = form1, error_text = 'Вы и так уже администратор.')

        user_password = User.get_password(session['username'])
        check = pbkdf2_sha256.verify(form1.password.data, user_password)
        if check != True:
            return render_template('king.html', all_users = all_users, role = role, form1 = form1, error_text = 'Вы ввели неправильный пароль.')

        for i in all_users:
            if form1.login.data == i.login:
                check1 = True
                if i.role == 'ban':
                    return render_template('king.html', all_users = all_users, role = role, form1 = form1, error_text = 'Этот пользователь забанен.', form2 = form2)
                if i.role == 'user':
                    return render_template('king.html', all_users = all_users, role = role, form1 = form1, error_text = 'Это обычный пользователь. Сначала он должен потренироваться в роли модератора.', form2 = form2)
                if i.role == 'admin':
                    return render_template('king.html', all_users = all_users, role = role, form1 = form1, error_text = 'Этот пользователь уже администратор.', form2 = form2)
                User.query.filter_by(login=i.login).update(dict(role='admin'))
                db.session.commit()
                return render_template('king.html', role = role, all_users = all_users, form1 = form1, success_text = 'Пользователь успешно добавлен в администраторы.', form2 = form2)

        if check1 != True:
            return render_template('king.html', all_users = all_users, role = role, form1 = form1, error_text = 'Пользователя с таким логином не существует.', form2 = form2)

    if form2.validate_on_submit():
        if form2.login.data != session['username']:
            return render_template('king.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text2 = 'Вы ввели неправильный логин.')

        user_password = User.get_password(session['username'])
        check = pbkdf2_sha256.verify(form2.password.data, user_password)
        if check != True:
            return render_template('king.html', all_users = all_users, role = role, form1 = form1, form2 = form2, error_text2 = 'Вы ввели неправильный пароль.')

        User.query.filter_by(login=session['username']).update(dict(role='user'))
        db.session.commit()
        return redirect('/account')
    return render_template('king.html', all_users = all_users, role = role, form1 = form1, form2 = form2)

# Страница 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
