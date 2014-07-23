# -*- coding: utf-8 -*-
from flask import redirect, request, url_for
from flask_app import app, db_connection, dbTables
from flask.ext import admin, login
from flask.ext.admin import helpers, expose
from flask.ext.admin.contrib import sqla
from forms import LoginForm, get_user

# initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db_connection.session.query(dbTables.Users).get(user_id)


# customized index view class that handles login
class CustomAdminIndexView(admin.AdminIndexView):

    __ViewMenuFlag = False

    def is_visible(self):
        return self.__ViewMenuFlag

    def __setFlag(self, value):
        self.__ViewMenuFlag = value

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            self.__setFlag(True)
            return redirect(url_for('.login_view'))
        return super(CustomAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):

        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = get_user(form.login.data)
            login.login_user(user)

        if login.current_user.is_authenticated():
            self.__setFlag(True)
            return redirect(url_for('.index'))

        self.__setFlag(False)
        self._template_args['form'] = form
        return super(CustomAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        self.__setFlag(False)
        login.logout_user()
        return redirect(url_for('.index'))


class UsersAdmin(sqla.ModelView):
    can_create = False
    can_delete = False
    form_columns = ['name', 'fullname', 'password', 'email', 'subscription_time_left']
    column_filters = ('name', 'fullname', 'password', 'email', 'subscription_time_left')

    def is_accessible(self):
        return login.current_user.is_authenticated()


class AccountTypeAdmin(sqla.ModelView):
    can_create = False
    can_delete = False
    form_columns = ['name', 'cost', 'description']
    column_filters = ('name', 'cost', 'description')

    def is_accessible(self):
        return login.current_user.is_authenticated()


class GroupAdmin(sqla.ModelView):
    form_columns = ['name', 'permission']
    column_filters = ('name', 'permission')

    def is_accessible(self):
        return login.current_user.is_authenticated()


class CatalogAdmin(sqla.ModelView):
    can_create = False
    can_delete = False
    form_columns = ['directory_name', 'last_modified', 'public_folder']
    column_filters = ('directory_name', 'last_modified', 'public_folder')

    def is_accessible(self):
        return login.current_user.is_authenticated()


class FileSpaceAdmin(sqla.ModelView):
    can_create = False
    can_delete = False
    form_columns = ['storage_name', 'created_time', 'catalog_id']
    column_filters = ('storage_name', 'created_time', 'catalog_id')

    def is_accessible(self):
        return login.current_user.is_authenticated()


class FileAdmin(sqla.ModelView):
    can_create = False
    can_delete = False
    form_columns = ['original_name', 'server_name', 'file_hash', 'chunk_size', 'chunk_number']
    column_filters = ('original_name', 'server_name', 'file_hash', 'chunk_size', 'chunk_number')

    def is_accessible(self):
        return login.current_user.is_authenticated()


class FileServerAdmin(sqla.ModelView):
    form_columns = ['ip', 'port', 'status', 'last_online']
    column_filters = ('ip', 'port', 'status', 'last_online')

    def is_accessible(self):
        return login.current_user.is_authenticated()


init_login()
tables_category = unicode('Таблицы', 'utf-8')
admin = admin.Admin(app, 'Cloud storage', index_view=CustomAdminIndexView(), base_template='my_master.html')
admin.add_view(AccountTypeAdmin(dbTables.AccountType, db_connection.session, category=tables_category, name='Account type'))
admin.add_view(CatalogAdmin(dbTables.Catalog, db_connection.session, category=tables_category, name='Catalog'))
admin.add_view(GroupAdmin(dbTables.Group, db_connection.session, category=tables_category, name='Groups'))
admin.add_view(FileAdmin(dbTables.File, db_connection.session, category=tables_category, name='File'))
admin.add_view(FileServerAdmin(dbTables.FileServer, db_connection.session, category=tables_category, name='File server'))
admin.add_view(FileSpaceAdmin(dbTables.FileSpace, db_connection.session, category=tables_category, name='File space'))
admin.add_view(UsersAdmin(dbTables.Users, db_connection.session, category=tables_category, name='Users'))
