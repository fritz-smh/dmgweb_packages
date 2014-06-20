# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, flash
from flask import render_template, render_template_string

from flask_wtf import Form
from wtforms import TextField, HiddenField
from wtforms.validators import DataRequired

from dmgweb_packages.application import app, github, login_required
from dmgweb_packages.common.package import PackageChecker, SubmissionList, SubmissionError

import traceback


@app.route('/validate_package')
@login_required
def validate_package():
    print("Validate!")
    print(request.args)
    try:
        sub_list = SubmissionList()
        sub_list.validate(request.args["type"], request.args["name"], request.args["version"])
        flash("Package {0}_{1} in version {2} validated and removed from the submission list".format(request.args["type"], request.args["name"], request.args["version"]), "success")
    except:
        flash(traceback.format_exc())
    return redirect(url_for("submission_list")) 


