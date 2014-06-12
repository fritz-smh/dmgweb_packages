"""
    GitHub Example
    --------------

    Shows how to authorize users with Github.

"""


# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string

# Flask-Github for Oauth with Github
from flask.ext.github import GitHub

# Flask-bootstrap
from flask_bootstrap import Bootstrap
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField, IntegerField, FormField, validators
from wtforms.validators import Required

# Sqlalchemy used for the user token storage with Oauth (and so Github)
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


##### Global vars

DOMOGIK_ORGANISATION = "Domogik"


##### Flask-Github related actions 

# Database configuration for Oauth (and so github)
DATABASE_URI = 'sqlite:////tmp/github-flask.db'
SECRET_KEY = 'development key'
DEBUG = True

# Set these values
GITHUB_CLIENT_ID = 'b3c8577a5e9a648cfebd'
GITHUB_CLIENT_SECRET = '05a933b4572b24bd0621b62820674a076dd12ca7'
GITHUB_CALLBACK_URL = 'http://les-cours-du-chaos.hd.free.fr/github-callback'

# setup flask
app = Flask(__name__)
app.config.from_object(__name__)

# setup github-flask
github = GitHub(app)

# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

###### Flask-bootstrap related actions

Bootstrap(app)



###### Database part

def init_db():
    Base.metadata.create_all(bind=engine)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(200))
    github_access_token = Column(Integer)

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token

###### Decorators

@app.before_request
def before_request():
    g.user = None
    g.username = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        g.username = github.get('user')['login']


@app.after_request
def after_request(response):
    db_session.remove()
    return response


### Views
from views.index import * 
from views.core_team import * 
from views.github import * 
from views.packages import * 
from views.user import * 

### main
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host = "192.168.1.10", port = 80)

