# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, flash
from flask import render_template, render_template_string

from flask_wtf import Form
from wtforms import TextField, HiddenField
from wtforms.validators import DataRequired

from dmgweb_packages.application import app, github, login_required, core_team_required
from dmgweb_packages.common.package import PackageChecker, SubmissionList, SubmissionError

import traceback


@app.route('/refuse_package', methods=['POST'])
@login_required
@core_team_required
def refuse_package():
    print request.method
    print request.form
    try:
        sub_list = SubmissionList()
        sub_list.refuse(request.form["type"], request.form["name"], request.form["version"], g.username, request.form["reason"])
        flash("Package {0}_{1} in version {2} refused and removed from the submission list".format(request.form["type"], request.form["name"], request.form["version"]), "success")
    except:
        flash(traceback.format_exc())
    return redirect(url_for("submission_list")) 


