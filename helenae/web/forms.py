# -*- coding: utf-8 -*-
from hashlib import sha256
from flask_app import app, db_connection, dbTables
from wtforms import form, fields, validators


RequireInput = u'Это поле должно быть заполнено'


class LoginForm(form.Form):
    login = fields.TextField(u"Логин", validators=[validators.InputRequired(RequireInput)])
    password = fields.PasswordField(u"Пароль", validators=[validators.InputRequired(RequireInput)])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            print 'here!'
            raise validators.ValidationError(unicode("Такого пользователя не существует!", 'utf-8'))

        admins_gr = self.get_group()
        if user.group_id != admins_gr.id:
            raise validators.ValidationError(unicode("Вы не администратор!", 'utf-8'))

    def validate_password(self, field):
        user = self.get_user()
        if user is not None:
            hash_psw = str(sha256(str(self.password.data)+str(user.id)).hexdigest())
            if user.password != hash_psw:
              raise validators.ValidationError(unicode("Некорректный пароль!", 'utf-8'))

    def get_user(self):
        return db_connection.session.query(dbTables.Users).filter_by(name=self.login.data).first()

    def get_group(self):
        return db_connection.session.query(dbTables.Group).filter_by(name='admins').first()