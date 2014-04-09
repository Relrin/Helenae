from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from db import tables as dbTables

app = Flask(__name__, template_folder='./web/templates/')
app.config['SECRET_KEY'] = 'some_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/csan'
db_connection = SQLAlchemy(app)

import web.admin
import web.views