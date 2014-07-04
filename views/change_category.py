# Flask common imports
from flask import Flask, request, g, session, redirect, url_for, flash
from flask import render_template, render_template_string

from flask_wtf import Form
from wtforms import TextField, HiddenField
from wtforms.validators import DataRequired

from dmgweb_packages.application import app, github, login_required, core_team_required
from dmgweb_packages.common.package import PackagesList, PackagesListError

import traceback


@app.route('/change_category', methods=['POST'])
@login_required
@core_team_required
def change_category():
    print("Change the category!")
    print(request.form)
    try:
        pkg_list = PackagesList()
        pkg_list.set_category(request.form["type"], request.form["name"], request.form["version"], request.form["category"])
        flash("Package {0}_{1} in version {2} category set to '{3}'".format(request.form["type"], request.form["name"], request.form["version"], request.form["category"]), "success")
    except:
        flash(traceback.format_exc())
    return redirect(url_for("packages")) 
