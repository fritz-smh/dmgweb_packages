"""
    GitHub Example
    --------------

    Shows how to authorize users with Github.

"""

import sys

if len(sys.argv) > 1 and sys.argv[1] == "build":
    BUILD = True
else:
    BUILD = False

# Flask common imports
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template, render_template_string


# Flask-Github for Oauth with Github
if not BUILD:
    from flask.ext.github import GitHub
else:
    from flask_frozen import Freezer

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


##### common libs

from dmgweb_packages.common.config import get_root_repository_url
if not BUILD:
    from dmgweb_packages.common.auth import is_core_team_member
from functools import wraps
import logging

##### Global vars

DOMOGIK_ORGANISATION = "Domogik"
LOG_FOLDER = "./logs/"
#LOG_FOLDER = "/tmp/"


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
if not BUILD:
    github = GitHub(app)

# setup Flask-frozen
else:
    app.config['FREEZER_RELATIVE_URLS'] = True
    #freezer = Freezer(app)

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logging.debug("Login required for this url. g.user = {0}".format(g.user))
        if g.user is None:
            logging.debug("Redirect to the login url")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def core_team_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logging.debug("Core team member required for this url.g.core_team = {0}".format(g.core_team))
        if not g.core_team:
            logging.warning("Access denied to this url (core team only). Redirect to the index url")
            flash("Access denied !")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def before_request():
    g.user = None
    g.username = None
    g.build = None
    if not BUILD:
        if 'user_id' in session:
            # get user informations
            g.user = User.query.get(session['user_id'])
            g.username = github.get('user')['login']
            # is the user member of the Domogik organisation ?
            # True or False
            g.core_team = is_core_team_member(github, DOMOGIK_ORGANISATION, g.username)
    else:
        g.build = True
        g.root_repository_url = get_root_repository_url()


@app.after_request
def after_request(response):
    db_session.remove()
    return response





### Views
from dmgweb_packages.views.index import * 
from dmgweb_packages.views.packages import * 
from dmgweb_packages.views.submission_list import * 
from dmgweb_packages.views.icons import * 
from dmgweb_packages.views.dashboard import * 

if not BUILD:
    from dmgweb_packages.views.change_category import * 
    from dmgweb_packages.views.core_team import * 
    from dmgweb_packages.views.delete_package import * 
    from dmgweb_packages.views.github import * 
    from dmgweb_packages.views.refused_list import * 
    from dmgweb_packages.views.user import * 
    from dmgweb_packages.views.submit_package import * 
    from dmgweb_packages.views.refuse_package import * 
    from dmgweb_packages.views.validate_package import * 


### main
if __name__ == '__main__':
    # logging
    logging.basicConfig(filename='{0}/dmgweb_package.log'.format(LOG_FOLDER), level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info('Starting!')
    print("Starting! Logs are in '{0}/dmgweb_package.log'".format(LOG_FOLDER))

    if not BUILD:
        init_db()
        app.run(debug=True, host = "192.168.1.10", port = 80)
    else:
        freezer = Freezer(app)

        @freezer.register_generator
        def icons_generator():
            the_icons = next(os.walk('data/icons'))[2]
            for an_icon in the_icons:
               yield 'icons', {'filename': an_icon }

        freezer.freeze()

