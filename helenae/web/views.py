# -*- coding: utf-8 -*-
import datetime
from hashlib import sha256
from time import gmtime, strftime

import sqlalchemy
from flask import render_template, redirect, url_for
from flask_app import app, db_connection, dbTables
from forms import RegisterForm


@app.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html', title=u"Главная")


@app.route('/success', methods=('GET', 'POST'))
def success():
    return render_template('success.html', title=u"Регистрация завершена!")


@app.route('/sign-up', methods=('GET', 'POST'))
def sign_up():
    form = RegisterForm()
    if form.validate_on_submit():
        # new catalog for user
        catalog_name = str(form.data['login'] + "_main")
        new_dir = dbTables.Catalog(catalog_name)
        db_connection.session.add(new_dir)
        db_connection.session.commit()
        # new filespace for user
        fs_name = str(form.data['login'] + "_fs")
        new_fs = dbTables.FileSpace(fs_name, new_dir)
        db_connection.session.add(new_fs)
        db_connection.session.commit()
        fs = db_connection.session.execute(
            sqlalchemy.select([dbTables.FileSpace])
                      .where(dbTables.FileSpace.storage_name == fs_name))
        fs = fs.fetchone()
        time_is = datetime.datetime.strptime(strftime("%d-%m-%Y", gmtime()),
                                             "%d-%m-%Y").date()
        time_is = time_is + datetime.timedelta(days=365)
        date_max = time_is.strftime("%Y-%m-%d")
        id_new = db_connection.session.execute(
            sqlalchemy.func.count(dbTables.Users.id)
        ).fetchone()[0] + 1
        password_hash = str(sha256(form.data['password'] +
                                   str(id_new)).hexdigest())
        # create new user
        new_user = dbTables.Users(form.data['login'], form.data['fullname'],
                                  password_hash, form.data['email'],
                                  date_max, 1, 2, fs.id)
        db_connection.session.add(new_user)
        db_connection.session.commit()
        return redirect(url_for('success'))
    return render_template('sign-up.html', title=u"Регистрация", form=form)


@app.route('/sign-in', methods=('GET', 'POST'))
def sign_in():
    return render_template('sign-in.html', title=u"Аутентификация")


@app.route('/forgot-password', methods=('GET', 'POST'))
def forgot_password():
    return render_template('forgot-password.html', title=u"Восстановление "
                                                         u"доступа")