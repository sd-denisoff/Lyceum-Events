from flask_wtf import FlaskForm
from wtforms import StringField, DateField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo
import re


# Форма авторизации
class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired(message='Это обязательное поле')])
    password = StringField('password', validators=[DataRequired(message='Это обязательное поле')])


# Форма регистрации
class RegForm(FlaskForm):
    pattern = '^[A-Za-z0-9_-]*$'
    def latinic(form, field):
        if not re.match(RegForm.pattern, field.data):
            raise ValidationError('Логин должен состоять из латинских букв, цифр, точки, дефиса или нижнего подчеркивания')

    name = StringField('name', validators=[DataRequired(message='Это обязательное поле')])
    email = StringField('email', validators=[DataRequired(message='Это обязательное поле')])
    login = StringField('login', validators=[DataRequired(message='Это обязательное поле'), latinic])
    password = StringField('password', validators=[DataRequired(message='Это обязательное поле'), Length(8, message='Количество символов должно превышать 8')])
    confirm = StringField('confirm', validators=[DataRequired(message='Это обязательное поле'), Length(8, message='Количество символов должно превышать 8'), EqualTo('password', message='Пароли должны совпадать')])


# Форма смены пароля
class ChangePasswordForm(FlaskForm):
    old_password = StringField('old_password', validators=[DataRequired(message='Это обязательное поле')])
    new_password = StringField('new_password', validators=[DataRequired(message='Это обязательное поле'), Length(8, message='Количество символов должно превышать 8')])
    confirm_new_password = StringField('confirm_new_password', validators=[DataRequired(message='Это обязательное поле'), EqualTo('new_password', message='Пароли должны совпадать'), Length(8, message='Количество символов должно превышать 8')])


# Форма смены почты
class ChangeMailForm(FlaskForm):
    password = StringField('password', validators=[DataRequired(message='Это обязательное поле')])
    old_email = StringField('old_email', validators=[DataRequired(message='Это обязательное поле')])
    new_email = StringField('new_email', validators=[DataRequired(message='Это обязательное поле')])


# Форма восстановления пароля
class ForgetPasswordForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(message='Это обязательное поле')])


# Форма бана юзера
class BanUserForm(FlaskForm):
    login = StringField('login', validators=[DataRequired(message='Это обязательное поле')])


# Форма помилования юзера
class AmnestyUserForm(FlaskForm):
    login = StringField('login', validators=[DataRequired(message='Это обязательное поле')])


# Форма добавления админа
class AddAdminForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired(), Length(8, message='Количество символов должно превышать 8')])
    confirm = StringField('confirm', validators=[DataRequired(), Length(8, message='Количество символов должно превышать 8'), EqualTo('password', message='Пароли должны совпадать')])


# Форма удаления админа
class RemoveAdminForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired(), Length(8, message='Количество символов должно превышать 8')])
    confirm = StringField('confirm', validators=[DataRequired(), Length(8, message='Количество символов должно превышать 8'), EqualTo('password', message='Пароли должны совпадать')])


# Форма создания мероприятия
class CreateEventForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(message='Это обязательное поле'), Length(3, message='Количество символов должно превышать 3')])
    content = StringField('content', validators=[DataRequired(message='Это обязательное поле'), Length(5, message='Количество символов должно превышать 5')])
    date = StringField('date', validators=[DataRequired(message='Это обязательное поле')])


# Форма отзыва
class FeedbackForm(FlaskForm):
    content = StringField('content', validators=[DataRequired(message='Это обязательное поле.'), Length(10, message='Количество символов должно превышать 10')])