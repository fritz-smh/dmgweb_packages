# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, flash
from flask import render_template, render_template_string

from flask_wtf import Form
from wtforms import TextField, HiddenField, SelectField
from wtforms.validators import DataRequired

from dmgweb_packages.application import app, github, login_required
from dmgweb_packages.common.package import PackageChecker, SubmissionList, SubmissionError
from dmgweb_packages.common.category import Categories, CategoriesError
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
import logging



### Forms

class FormSubmitPackage(Form):

    # prepare some data
    categories = Categories()
    
    # form
    url_package = TextField('url_package', validators=[DataRequired()])
    url_build_status = TextField('url_build_status')
    url_doc = TextField('url_doc')
    package = HiddenField('package')
    type = HiddenField('type')
    name = HiddenField('name')
    version = HiddenField('version')
    description = HiddenField('description')
    author = HiddenField('author')
    author_email = HiddenField('author_email')
    tags = HiddenField('tags')
    json_version = HiddenField('json_version')
    domogik_min_version = HiddenField('domogik_min_version')
    hash_sha256 = HiddenField('hash_sha256')
    step = HiddenField('step')
    category = SelectField('category', choices=categories.list_for_wtf())


@app.route('/submit_package', methods=['GET', 'POST'])
@login_required
def submit_package():
    # TODO : reactivate CSRF !!!!
    form = FormSubmitPackage(request.form, csrf_enabled=False)
    
    print request.form
    if form.validate_on_submit() and form.step.data == '1':
        ### data from the form
        url_package = form.url_package.data
        url_build_status = form.url_build_status.data

        ### build data from the form
        # TODO : try to get version from the info.json from the zip file
        submitter = g.username

        ### try to get the remote zip file
        the_package = PackageChecker(url_package)
        ok, message = the_package.download()
        if not ok:
            flash(message, "error")
        else:
            ok, message = the_package.get_info_json()
            if not ok:
                flash(message, "error")
            else:
                try:
                    form.step.data                = '2'
                    form.version.data             = the_package.get_json()['identity']['version']
                    form.type.data                = the_package.get_json()['identity']['type']
                    form.name.data                = the_package.get_json()['identity']['name']
                    form.package.data             = "{0}_{1}".format(form.type.data, form.name.data)
                    form.description.data         = the_package.get_json()['identity']['description']
                    form.tags.data                = ",".join(the_package.get_json()['identity']['tags'])
                    form.author.data              = the_package.get_json()['identity']['author']
                    form.author_email.data        = the_package.get_json()['identity']['author_email']
                    form.hash_sha256.data         = the_package.get_json()['hash_sha256']
                    form.json_version.data        = the_package.get_json()['json_version']
                    form.domogik_min_version.data = the_package.get_json()['identity']['domogik_min_version']
                    # submitter
                    # remarks
                except:
                    flash("It seems there is an error in the json : {0}".format(traceback.format_exc()))
                
        try:
            the_package.delete_downloaded_file()
        except:
            # if we can't delete the tmp file, never mind...
            pass
        return render_template('submit_package.html', form = form, step = 2)

    elif form.validate_on_submit() and form.step.data == '2':
        success = False
        submitted_package = { "url_package" : form.url_package.data,
                              "category" : form.category.data,
                              "url_build_status" : form.url_build_status.data,
                              "url_doc" : form.url_doc.data,
                              "package" : form.package.data,
                              "type" : form.type.data,
                              "name" : form.name.data,
                              "version" : form.version.data,
                              "description" : form.description.data,
                              "tags" : form.tags.data,
                              "author" : form.author.data,
                              "author_email" : form.author_email.data,
                              "hash_sha256" : form.hash_sha256.data,
                              "json_version" : form.json_version.data,
                              "domogik_min_version" : form.domogik_min_version.data,
                              "submitter" : g.username,
                              "submission_date" : time.time()
                            }
        try:
            submission_list = SubmissionList()
            submission_list.add(submitted_package)
            submission_list.list()
            success = True
        except SubmissionError as e: 
            flash(e.value, "error")
        except:
            flash(traceback.format_exc(), "error")
        return render_template('submit_package.html', form = form, step = 3, success = success)
    else:
        form.step.data = '1'
        return render_template('submit_package.html', form = form, step = 1)


