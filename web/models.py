from web import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(256), unique=True)
    login = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256))
    role = db.Column(db.String(120), default='no')

    def __init__(self, name, email, login, password):
        self.name = name
        self.email = email
        self.login = login
        self.password = password

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self.id

    # Получает список всех пользователей
    @staticmethod
    def get_all():
        return User.query.all()

    # Получение почты пользователя по логину
    @staticmethod
    def get_email(s):
        users = User.query.all()
        for i in users:
            if s == i.login:
                return i.email

    # Получение хэш-пароля по логину
    @staticmethod
    def get_password(s):
        users = User.query.all()
        for i in users:
            if s == i.login:
                return i.password

    # Получение имени по логину
    @staticmethod
    def get_name(s):
        users = User.query.all()
        for i in users:
            if s == i.login:
                return i.name

    # Получение id пользователя по логину
    @staticmethod
    def get_myid(s):
        users = User.query.all()
        for i in users:
            if s == i.login:
                return i.id

    # Получение роли по логину
    @staticmethod
    def get_role(s):
        users = User.query.all()
        for i in users:
            if s == i.login:
                return i.role


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128))
    content = db.Column(db.String(256))
    date = db.Column(db.String(256))
    members = db.Column(db.Integer, default=0)
    author_login = db.Column(db.String(128), db.ForeignKey('user.login'))
    author = db.relationship('User', backref=db.backref('events'))

    def __init__(self, title, content, date, author_login):
        self.title = title
        self.content = content
        self.date = date
        self.author_login = author_login

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self.id

    # Получает список всех мероприятий
    @staticmethod
    def get_all():
        events = list(reversed(Event.query.all()))
        return events

    # Получает список мероприятий, созданных конкретным пользователем
    @staticmethod
    def get_user_events(login):
        events = Event.query.all()
        user_events = []
        for event in events:
            if event.author_login == login:
                user_events.append(event)
        user_events.reverse()
        return user_events

    # Получает мероприятие по его id
    @staticmethod
    def get_event(id):
        events = Event.query.all()
        for event in events:
            if event.id == id:
                return event


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(526))
    author = db.Column(db.String(256))

    def __init__(self, content, author):
        self.content = content
        self.author = author

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self.id

    @staticmethod
    def get_all():
        return Feedback.query.all()
