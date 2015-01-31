from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask.ext.babelex import Babel
from db import tables as dbTables
from db.queries import engine as db_engine

app = Flask(__name__, template_folder='./web/templates/', static_folder='./web/static/', static_url_path='')
app.config['SECRET_KEY'] = 'some_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/csan'
db_connection = SQLAlchemy(app)

# Initialize babel
babel = Babel(app)
@babel.localeselector
def get_locale():
    override = request.args.get('lang')
    if override:
        session['lang'] = override
    return session.get('lang', 'ru')

import web.admin
import web.views

if __name__ == "__main__":
    from web.admin import *
    from web.views import *
    app.run(port=8000, debug=True)