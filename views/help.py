# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, flash
from flask import render_template, render_template_string

from flask_wtf import Form
from wtforms import TextField, HiddenField, SelectField
from wtforms.validators import DataRequired

from dmgweb_packages.application import app, github, login_required
from dmgweb_packages.common.package import PackageChecker, PackageError
import json
import os
import sys
import traceback
import requests
import re
import time








@app.route('/help_documentation', methods=['GET'])
@login_required
def help_documentation():
    app.logger.debug(u"Calling /help_documentation")
    app.logger.debug(u"Method='{0}', form='{1}'".format(request.method, request.form))

    return render_template('help_documentation.html')

@app.route('/help_domogik_max_release', methods=['GET'])
@login_required
def help_domogik_max_release():
    app.logger.debug(u"Calling /help_domogik_max_release")
    app.logger.debug(u"Method='{0}', form='{1}'".format(request.method, request.form))

    return render_template('help_domogik_max_release.html')

@app.route('/help_report_an_issue', methods=['POST'])
@login_required
def help_report_an_issue():
    app.logger.debug(u"Calling /help_report_an_issue")
    app.logger.debug(u"Method='{0}', form='{1}'".format(request.method, request.form))

    try:
        pkg_type = request.form['type']
        pkg_name = request.form['name']
        pkg_release = request.form['release']
        pkg_new_issue_url = app.packages.get_new_issue_url(pkg_type, pkg_name)
    except:
        app.logger.error(u"Error while getting package informations. Error is : {0}".format(traceback.format_exc()))
        # TODO: dedicated error page
        # TODO: dedicated error page
        # TODO: dedicated error page
        return render_template('error.html')

    return render_template('help_report_an_issue.html',
                            name = pkg_name,
                            type = pkg_type,
                            release = pkg_release,
                            new_issue_url = pkg_new_issue_url)


@app.route('/help_lock', methods=['GET'])
@login_required
def help_lock():
    app.logger.debug(u"Calling /help_lock")
    app.logger.debug(u"Method='{0}', form='{1}'".format(request.method, request.form))

    return render_template('help_lock.html')


