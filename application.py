#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
dmgweb_packages
A repository to host domogik packages
"""

import sys

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

# Flask Babel - i18n
from flask import Flask
from flask.ext.babel import Babel


##### common libs

from dmgweb_packages.common.package import Packages
from dmgweb_packages.common.config import Config
from dmgweb_packages.common.auth import is_core_team_member, get_github_oauth_data
from functools import wraps
import logging
import os
import datetime

##### Global vars

PWD = os.path.dirname(os.path.realpath(__file__))
LOG_FOLDER = "{0}/logs/".format(PWD)


##### Flask-Github related actions 

# Database configuration for Oauth (and so github)
DATABASE_URI = 'sqlite:////{0}/github-flask.db'.format(PWD)
SECRET_KEY = 'development key'
DEBUG = True

# Set these values
GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_CALLBACK_URL, GITHUB_AUTH_SKIPPING = get_github_oauth_data()

# setup flask
app = Flask(__name__)
app.config.from_object(__name__)

# setup github-flask
github = GitHub(app)

# setup sqlalchemy for github oauth
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

###### Babel - i18n
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'

###### Flask-bootstrap related actions

Bootstrap(app)


###### Configuration part

app.my_config = Config()
app.next_url = "/"  # used by github login
app.GITHUB_AUTH_SKIPPING = GITHUB_AUTH_SKIPPING


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
        app.logger.debug("Login required for this url. g.user = {0}".format(g.user))
        if GITHUB_AUTH_SKIPPING == True:
            app.logger.warning("Development mode : AUTHENTICATION SKIPPED (see config.json => github>skip")
            # we skip the authentication : 'dev mode'
            pass
        else:
            # we DO the authentication
            if g.user is None:
                app.logger.debug("Redirect to the login url")
                return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# TODO: review
def core_team_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        app.logger.debug("Core team member required for this url. g.core_team = {0}".format(g.core_team))
        #if not g.core_team:
        #    app.logger.warning("Access denied to this url (core team only). Redirect to the index url")
        #    flash("Access denied !")
        #    return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def before_request():
    g.user = None
    g.username = None
    g.build = None
    if GITHUB_AUTH_SKIPPING == True:
        # we skip the authentication : 'dev mode'
        g.username = "@developper"
        g.core_team = True

    else:
        # we DO the authentication
        if 'user_id' in session:
            # get user informations
            g.user = User.query.get(session['user_id'])
            g.username = github.get('user')['login']
            app.logger.info("--- Before request | username = {0}".format(g.username))
            # is the user member of the Domogik organisation ?
            # True or False
            g.core_team = is_core_team_member(app.logger, g.username)


@app.after_request
def after_request(response):
    if 'user_id' in session:
        app.logger.info("--- After request | username = {0}".format(g.username))
    db_session.remove()
    return response


### formatters
@app.template_filter('datetime')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt is None:
        fmt = "%d %B %Y"
    return format(datetime.datetime.fromtimestamp(date), fmt)



### Errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500




# logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# logging - file handler
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
handler = logging.FileHandler("{0}/dmgweb_package.log".format(LOG_FOLDER), mode='a')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)


#app.logger.handlers.extend(log.handlers)
app.logger.setLevel(logging.DEBUG)

app.logger.debug("Starting...")
#print("Starting! Logs are in '{0}/dmgweb_package.log'".format(LOG_FOLDER))

# load packages
app.packages = Packages(app.logger)
# load domogik releases
app.domogik_releases = app.my_config.get_domogik_releases()




### Views
from dmgweb_packages.views.index import * 
from dmgweb_packages.views.data import * 
from dmgweb_packages.views.github import * 
from dmgweb_packages.views.packages_management import * 
from dmgweb_packages.views.icons import * 
from dmgweb_packages.views.help import * 
from dmgweb_packages.views.api_crontab import * 


### main
if __name__ == '__main__':
    # first, write the pid in a file
    with open("{0}/dmgweb_packages.pid".format(LOG_FOLDER), 'w') as pid_file:
        pid_file.write(str(os.getpid()))


    init_db()
    #app.run(debug=True, host = "192.168.1.10", port = 80)
    app.run(debug=True, host = app.my_config.get_server_ip(), port = app.my_config.get_server_port())

