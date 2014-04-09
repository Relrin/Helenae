from flask import redirect, request, url_for
from flask_app import app, db_connection, dbTables
from flask.ext import admin, login
from flask.ext.admin import helpers, expose
from forms import LoginForm

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

    def is_visible(self):
        return False

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(CustomAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):

        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))

        self._template_args['form'] = form
        return super(CustomAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))

init_login()
admin = admin.Admin(app, 'Cloud storage', index_view=CustomAdminIndexView(), base_template='my_master.html')