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
import tempfile
import magic
import zipfile
import time



class FormManageExistingPackage(Form):
    # prepare default data (will be updated when used)
    packages = app.packages.list()

    # form
    package = SelectField('package', choices=packages)
    step = HiddenField('step', default=1)

class FormManageNewPackage(Form):
    # form
    url = TextField('url')



@app.route('/manage_packages', methods=['GET', 'POST'])
@login_required
def manage_packages():
    app.logger.debug(u"Calling /manage_packages")
    app.logger.debug(u"Method='{0}', form='{1}'".format(request.method, request.form))
    form_existing = FormManageExistingPackage(csrf_enabled=True)
    form_existing.package.choices = app.packages.list()
    form_new = FormManageNewPackage(csrf_enabled=True)

    return render_template('manage_packages.html', 
                           form_existing = form_existing, 
                           form_new = form_new, 
                           step = 1)


@app.route('/manage_a_package', methods=['GET', 'POST'])
@login_required
def manage_a_package():
    app.logger.debug(u"Calling /manage_a_package")
    app.logger.debug(u"Method='{0}', form='{1}'".format(request.method, request.form))
    form_new = FormManageNewPackage(csrf_enabled=True)

    try:
        package_id = request.form['package']
        pkg_type = package_id.split("-")[0]
        pkg_name = package_id.split("-")[1]
        pkg_informations = app.packages.get_informations(pkg_type, pkg_name)

        # special case - the package does not exists
        if not app.packages.is_package_existing(pkg_type, pkg_name):
            return render_template('manage_a_package_no_package.html',
                                   package_id = package_id)

        pkg_releases = app.packages.get_releases(pkg_type, pkg_name)
        pkg_notes = app.packages.get_notes(pkg_type, pkg_name)
        pkg_new_issue_url = app.packages.get_new_issue_url(pkg_type, pkg_name)
        pkg_issues = app.packages.get_issues(pkg_type, pkg_name)
        pkg_pull_requests = app.packages.get_pull_requests(pkg_type, pkg_name)
    except:
        app.logger.error(u"Error while getting package informations. Error is : {0}".format(traceback.format_exc()))
        # TODO: dedicated error page
        # TODO: dedicated error page
        # TODO: dedicated error page
        return render_template('error.html')

    return render_template('manage_a_package.html', 
                           form_new = form_new,
                           package_id = package_id,
                           type = pkg_type,
                           name = pkg_name,
                           informations = pkg_informations,
                           releases = pkg_releases,
                           notes = pkg_notes,
                           new_issue_url = pkg_new_issue_url,
                           issues = pkg_issues,
                           pull_requests = pkg_pull_requests)



@app.route('/submit_new_package', methods=['GET', 'POST'])
@login_required
def submit_new_package():
    """ Only for a new package.
        2 steps : 
        - 1 : download the given package url thanks to /submit_new_package_async, display the form to get email and website
          (in this case, step='')
        - 2 : save the package and redirect to /submit_new_package_release with appropriate form values
          (in this case, step='save')
    """
    app.logger.info(u"Calling /submit_new_package")
    app.logger.debug(u"Method='{0}', form='{1}'".format(request.method, request.form))

    if request.method != 'POST':
        return render_template('error.html')

    ### Handle POST method
    if 'step' in request.form:
        step = request.form['step']
    else: 
        step = 'check'
    app.logger.info(u"Step = '{0}'".format(step))

    # common to all steps
    try:
        url = request.form['url']
    except:
        app.logger.error(u"Error while getting url value")
        return render_template('error.html')

    # step 1
    if step == 'check':
        return render_template('submit_new_package.html', 
                               url = url)

    # step 2
    elif step == 'save':
        # get values from form
        try:
            pkg_type = request.form['type']
            pkg_name = request.form['name']
            pkg_email = request.form['email']
            pkg_site = request.form['site']
        except:
            app.logger.error(u"Error while getting some value. Error is : {0}".format(traceback.format_exc()))
            return render_template('error.html')

        # create the package
        try:
            app.packages.add(pkg_type = pkg_type,
                             pkg_name = pkg_name,
                             pkg_email = pkg_email,
                             pkg_site = pkg_site)
        except PackageError as e:
            app.logger.error(u"Error while creating the package. Error is : {0}".format(e.value))
            return render_template('submit_new_package_error.html',
                                   error = e.value)
        except:
            app.logger.error(u"Error while creating the package. Error is : {0}".format(traceback.format_exc()))
            return render_template('submit_new_package_error.html',
                                   error = traceback.format_exc())

        # and now submit the package release...
        return render_template('submit_new_package_created.html', 
                               url = url)


@app.route('/submit_new_package_async', methods=['POST'])
@login_required
def submit_new_package_async():
    """ Background task called from /submit_new_package
    """
    app.logger.debug(u"Calling /submit_new_package_async")
    app.logger.debug(u"Method='{0}', form='{1}'".format(request.method, request.form))

    if request.method != 'POST':
        return render_template('error.html')

    ### Handle POST method
    try:
        url = request.form['url']
    except:
        app.logger.error(u"Error while getting url value")
        return render_template('error.html')

    # Download the package
    app.logger.debug(u"Instanciate PackageChecker for '{0}'".format(url))
    pkg_checker = PackageChecker(app.logger, url)
    app.logger.debug(u"Start downloading the package...")
    status, response = pkg_checker.download()
    if not status:
        app.logger.error(u"Error while downloading : {0}".format(response))
        return render_template('submit_new_package_async.html',
                               url = url,
                               error = response)

    app.logger.debug(u"Start reading the package json file...")
    status, response = pkg_checker.get_info_json()
    if not status:
        app.logger.error(u"Error while downloading : {0}".format(response))
        return render_template('submit_new_package_async.html',
                               url = url,
                               error = response)

    # Get needed informations from the json
    pkg_type =  pkg_checker.get_json()["identity"]["type"]
    pkg_name =  pkg_checker.get_json()["identity"]["name"]
    # We do some basic transformations on the email to get a usable one
    pkg_email =  pkg_checker.get_json()["identity"]["author_email"].replace(" at ", "@").replace(" chez ", "@").replace(" dot ", ".")

    # Try to guess the website url from the package url
    try:
        if url.startswith("https://github.com/"):
            user = url.split("/")[3]
            repo = url.split("/")[4]
            pkg_site = "https://github.com/{0}/{1}/".format(user, repo)
        else:
            pkg_site = ""
    except:
        app.logger.warning(u"Error while trying to build the website url from package release url '{0}'. Error is : {1}".format(url, traceback.format_exc()))
        pkg_site = ""

    return render_template('submit_new_package_async.html',
                           url = url,
                           error = None, 
                           type = pkg_type,
                           name = pkg_name,
                           email = pkg_email,
                           site = pkg_site)





@app.route('/submit_new_package_release', methods=['GET', 'POST'])
@login_required
def submit_new_package_release():
    """ Only for a new package release.
        - download the given package url thanks to /submit_new_package_release_async
        - launch the review
    """
    app.logger.debug(u"Calling /submit_new_package_release")
    app.logger.debug(u"Method='{0}', form='{1}'".format(request.method, request.form))

    if request.method != 'POST':
        return render_template('error.html')

    ### Handle POST method
    try:
        url = request.form['url']
        # new_package means that this is the first release submission and the package has just be created
        # This flag is used only for cosmetic
        if 'new_package' in request.form:
            new_package = True
        else:
            new_package = False
    except:
        app.logger.error(u"Error while getting url value")
        return render_template('error.html')


    return render_template('submit_new_package_release.html',
                           new_package = new_package,
                           url = url)


@app.route('/submit_new_package_release_async', methods=['POST'])
@login_required
def submit_new_package_release_async():
    """ Background task called from /submit_new_package_release
    """
    app.logger.debug(u"Calling /submit_new_package_release_async")
    app.logger.debug(u"Method='{0}', form='{1}'".format(request.method, request.form))

    if request.method != 'POST':
        return render_template('error.html')

    ### Handle POST method
    try:
        url = request.form['url']
    except:
        app.logger.error(u"Error while getting url value")
        return render_template('error.html')

    # Download the package
    app.logger.debug(u"Instanciate PackageChecker for '{0}'".format(url))
    pkg_checker = PackageChecker(app.logger, url)
    app.logger.debug(u"Start downloading the package...")
    status, response = pkg_checker.download()
    if not status:
        app.logger.error(u"Error while downloading : {0}".format(response))
        return render_template('submit_new_package_async.html',
                               url = url,
                               error = response)

    app.logger.debug(u"Start reading the package json file...")
    status, response = pkg_checker.get_info_json()
    if not status:
        app.logger.error(u"Error while downloading : {0}".format(response))
        return render_template('submit_new_package_async.html',
                               url = url,
                               error = response)

    # Get needed informations from the json
    try:
        pkg_type =  pkg_checker.get_json()["identity"]["type"]
        pkg_name =  pkg_checker.get_json()["identity"]["name"]
        pkg_release =  pkg_checker.get_json()["identity"]["version"]
    except:
        msg = u"Error while getting informations from json. Error is : {0}".format(traceback.format_exc())
        app.logger.error(msg)
        return render_template('submit_new_package_release_async.html',
                               url = url,
                               error = msg)
    # TODO : review
    # TODO : review
    # TODO : review

    try:
        app.packages.add_release(pkg_type, pkg_name, pkg_release, url)
    except PackageError as e:
        msg = u"Error while adding the package. Error is : {0}".format(e.value)
        app.logger.error(msg)
        return render_template('submit_new_package_release_async.html',
                               url = url,
                               error = msg)

    return render_template('submit_new_package_release_async.html',
                           url = url,
                           type = pkg_type,
                           name = pkg_name,
                           error = None)
