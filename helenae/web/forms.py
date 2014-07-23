# -*- coding: utf-8 -*-
import re
from hashlib import sha256
from flask_app import app, db_connection, dbTables
from flask_wtf import Form
from wtforms import fields
from wtforms.validators import DataRequired, ValidationError


def get_user(user):
    return db_connection.session.query(dbTables.Users).filter_by(name=user).first()


class LoginForm(Form):
    login = fields.TextField(u"Логин", validators=[DataRequired(),])
    password = fields.PasswordField(u"Пароль", validators=[DataRequired(),])

    def validate_login(self, field):
        user = get_user(self.login.data)

        if user is None:
            raise ValidationError(unicode("Такого пользователя не существует!", 'utf-8'))

        admins_gr = self.get_group()
        if user.group_id != admins_gr.id:
            raise ValidationError(unicode("Вы не администратор!", 'utf-8'))

    def validate_password(self, field):
        user = get_user(self.login.data)
        if user is not None:
            hash_psw = str(sha256(str(self.password.data)+str(user.id)).hexdigest())
            if user.password != hash_psw:
                raise ValidationError(unicode("Некорректный пароль!", 'utf-8'))

    def get_group(self):
        return db_connection.session.query(dbTables.Group).filter_by(name='admins').first()


class RegisterForm(Form):
    login = fields.TextField(u"Логин", validators=[DataRequired(),])
    password = fields.PasswordField(u"Пароль", validators=[DataRequired(),])
    fullname = fields.TextField(u"Ф.И.О.", validators=[DataRequired(),])
    email = fields.TextField(u"Ваш email адрес", validators=[DataRequired(),])

    def validate_login(self, field):
        new_user = self.login.data.replace(' ', '')
        self.login.data = new_user
        finded_user = get_user(new_user)
        if len(new_user) < 3:
            raise ValidationError(unicode("Логин содержит минимум 3 символа!", 'utf-8'))

        if finded_user is not None:
            raise ValidationError(unicode("Такой пользователь уже существует!", 'utf-8'))

    def validate_password(self, field):
        new_user_password = self.password.data
        new_user_password = new_user_password.replace(' ', '')
        new_user_password = new_user_password.translate("~|*:'><?!@#^&%=+`$[]{}," + '"')
        if len(new_user_password) < 6:
            raise ValidationError(unicode("Пароль состоит минимум из 6 символов!", 'utf-8'))

    def validate_fullname(self, field):
        new_user_fullname = self.fullname.data
        new_user_fullname = new_user_fullname.strip()
        new_user_fullname = new_user_fullname.translate("~|*:'><?!@#^&%=+`$[]{}," + '"')
        new_user_fullname = filter(lambda x: x!= '', new_user_fullname.split(' '))
        new_user_fullname = ' '.join(new_user_fullname)
        self.fullname.data = new_user_fullname
        if len(new_user_fullname) < 5:
            raise ValidationError(unicode("Ф.И.О. состоит минимум из 5 символов!", 'utf-8'))

    def validate_email(self, field):
        regexp_mail = '[\.\w]{1,}[@]\w+[.]\w+'
        new_user_email = self.email.data.replace(' ', '')
        self.email.data = new_user_email
        if re.match(regexp_mail, new_user_email) is None:
            raise ValidationError(unicode("Указанный email неккоректен!", 'utf-8'))
